"""Text chunking service using tiktoken"""

from typing import List, Tuple

import tiktoken

from app.core.config import get_settings

settings = get_settings()


def chunk_text(
    text: str,
    page_num: int,
    chunk_size: int = None,
    overlap: int = None
) -> List[Tuple[int, str]]:
    """
    Chunk text into smaller pieces based on token count

    Args:
        text: Text to chunk
        page_num: Page number for this text
        chunk_size: Maximum tokens per chunk (from settings if not provided)
        overlap: Token overlap between chunks (from settings if not provided)

    Returns:
        List of tuples (page_number, chunk_text)
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_TOKEN_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP

    # Use cl100k_base encoding (used by GPT-4, GPT-3.5-turbo)
    encoding = tiktoken.get_encoding("cl100k_base")

    # Encode text to tokens
    tokens = encoding.encode(text)

    # If text is smaller than chunk size, return as is
    if len(tokens) <= chunk_size:
        return [(page_num, text)]

    chunks = []
    start = 0

    while start < len(tokens):
        # Get chunk tokens
        end = start + chunk_size
        chunk_tokens = tokens[start:end]

        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append((page_num, chunk_text))

        # Move start position with overlap
        start = end - overlap

    return chunks


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text for a specific model

    Args:
        text: Text to count tokens for
        model: Model name (for encoding selection)

    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Default to cl100k_base if model not found
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))
