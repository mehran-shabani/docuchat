"""Prometheus metrics endpoint"""

from typing import Dict

from fastapi import APIRouter, Depends
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.responses import Response

from app.db.session import AsyncSession, get_db

router = APIRouter()

# Metrics definitions
openai_tokens_total = Counter(
    "openai_tokens_total",
    "Total OpenAI tokens consumed",
    ["tenant", "direction", "model"],
)

ml_fallback_total = Counter(
    "ml_fallback_total", "Total ML model fallbacks", ["from_model", "to_model", "tenant"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "status"],
)

openai_request_total = Counter(
    "openai_request_total",
    "Total OpenAI API requests",
    ["tenant", "model", "status"],
)

openai_request_duration_seconds = Histogram(
    "openai_request_duration_seconds",
    "OpenAI API request duration in seconds",
    ["tenant", "model"],
)

rag_query_total = Counter(
    "rag_query_total", "Total RAG queries processed", ["tenant", "model"]
)

document_chunks_total = Counter(
    "document_chunks_total", "Total document chunks stored", ["tenant"]
)


@router.get("/metrics")
async def metrics_endpoint():
    """
    Expose Prometheus metrics.

    Returns metrics in Prometheus exposition format for scraping.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/metrics/health")
async def metrics_health(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """
    Health check for metrics endpoint.

    Returns:
        Dict with status
    """
    return {"status": "healthy", "service": "metrics"}
