"""PDF ingestion service using pypdf"""

from io import BytesIO
from typing import List, Tuple

from pypdf import PdfReader


async def extract_text_from_pdf(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Extract text from PDF file

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        List of tuples (page_number, text_content)

    Raises:
        ValueError: If PDF is invalid or exceeds limits
    """
    try:
        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)

        num_pages = len(reader.pages)

        # Check page limit
        from app.core.config import get_settings

        settings = get_settings()

        if num_pages > settings.MAX_PDF_PAGES:
            raise ValueError(
                f"PDF has {num_pages} pages, maximum allowed is {settings.MAX_PDF_PAGES}"
            )

        # Extract text from each page
        pages_text = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():  # Only include non-empty pages
                pages_text.append((page_num, text))

        return pages_text

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}") from e
