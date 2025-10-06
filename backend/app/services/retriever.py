"""Vector retrieval service for RAG"""

from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedder import create_embedding
from app.core.config import get_settings

settings = get_settings()


async def retrieve_relevant_chunks(
    query: str,
    tenant_id: int,
    session: AsyncSession,
    top_k: int = None
) -> List[Tuple[str, int, str]]:
    """
    Retrieve most relevant chunks for a query using vector similarity
    
    Args:
        query: User query
        tenant_id: Tenant ID for scoping
        session: Database session
        top_k: Number of chunks to retrieve (from settings if not provided)
    
    Returns:
        List of tuples (chunk_text, page_number, document_title)
    """
    if top_k is None:
        top_k = settings.TOP_K
    
    # Create embedding for query
    query_embedding = await create_embedding(query)
    
    # Convert embedding to PostgreSQL array format
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    # Query for similar chunks with tenant scoping
    query_sql = text("""
        SELECT 
            c.text,
            c.page,
            d.title,
            (c.embedding <=> :embedding::vector) AS distance
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE d.tenant_id = :tenant_id
        ORDER BY c.embedding <=> :embedding::vector
        LIMIT :limit
    """)
    
    result = await session.execute(
        query_sql,
        {
            "embedding": embedding_str,
            "tenant_id": tenant_id,
            "limit": top_k
        }
    )
    
    rows = result.fetchall()
    
    return [(row[0], row[1], row[2]) for row in rows]
