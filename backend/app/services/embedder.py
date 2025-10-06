"""Embedding service using OpenAI"""

from typing import List

from openai import AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None,
)


async def create_embedding(text: str) -> List[float]:
    """
    Create embedding vector for text using OpenAI

    Args:
        text: Text to embed

    Returns:
        Embedding vector (list of floats)
    """
    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


async def create_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings for multiple texts in batch

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
    )

    # Sort by index to maintain order
    sorted_embeddings = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_embeddings]
