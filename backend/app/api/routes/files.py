"""File upload routes"""

import time
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_session
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.files import UploadOut
from app.services.chunker import chunk_text
from app.services.embedder import create_embeddings_batch
from app.services.pdf_ingest import extract_text_from_pdf

settings = get_settings()
router = APIRouter()


async def process_pdf_file(
    file_bytes: bytes,
    title: str,
    tenant_id: int,
    document_id: int
):
    """
    Background task to process PDF file

    Args:
        file_bytes: PDF file content
        title: Document title
        tenant_id: Tenant ID
        document_id: Document ID to update
    """
    from app.db.session import async_session_maker

    async with async_session_maker() as session:
        try:
            # Extract text from PDF
            pages_text = await extract_text_from_pdf(file_bytes)

            # Chunk all pages
            all_chunks = []
            for page_num, text in pages_text:
                chunks = chunk_text(text, page_num)
                all_chunks.extend(chunks)

            # Create embeddings in batch
            chunk_texts = [chunk[1] for chunk in all_chunks]
            embeddings = await create_embeddings_batch(chunk_texts)

            # Save chunks to database
            for (page_num, text_content), embedding in zip(all_chunks, embeddings):
                chunk = Chunk(
                    document_id=document_id,
                    page=page_num,
                    text=text_content,
                    embedding=embedding
                )
                session.add(chunk)

            await session.commit()

        except Exception as e:
            print(f"[ERROR] Failed to process PDF {document_id}: {str(e)}")
            # In production, update document status to 'failed'


@router.post("", response_model=UploadOut)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload a PDF file and process it for RAG

    Extracts text, chunks it, creates embeddings, and stores in database
    """
    start_time = time.time()

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Read file content
    file_bytes = await file.read()

    # Check file size
    file_size_mb = len(file_bytes) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {file_size_mb:.2f}MB exceeds maximum {settings.MAX_FILE_SIZE_MB}MB"
        )

    # Use filename as title if not provided
    if not title:
        title = file.filename

    tenant_id = current_user["tenant_id"]

    try:
        # Quick validation - extract page count
        pages_text = await extract_text_from_pdf(file_bytes)
        num_pages = len(pages_text)

        # Create document record
        document = Document(
            tenant_id=tenant_id,
            title=title,
            pages=num_pages
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)

        # Process in background
        background_tasks.add_task(
            process_pdf_file,
            file_bytes,
            title,
            tenant_id,
            document.id
        )

        elapsed_ms = (time.time() - start_time) * 1000

        # Return preliminary response
        # Actual chunk count will be available after background processing
        return UploadOut(
            document_id=document.id,
            chunks=0,  # Will be updated in background
            elapsed_ms=elapsed_ms
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )
