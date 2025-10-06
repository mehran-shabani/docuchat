"""Middleware for tracking HTTP request metrics"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes.metrics import http_request_duration_seconds


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request duration and status codes"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track request duration and status code.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response from the handler
        """
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Record metrics
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).observe(duration)

        return response
