"""FastAPI application main entry point"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import api_router
from app.core.config import get_settings
from app.db.init import setup_pgvector
from app.db.session import init_db
from app.middleware.metrics import MetricsMiddleware
from app.services.ratelimit import limiter
from app.ws.chat import websocket_chat_handler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    should_skip_startup = os.getenv(
        "DISABLE_STARTUP_INIT"
    ) == "1" or settings.DATABASE_URL.startswith("sqlite")
    if should_skip_startup:
        print("[STARTUP] Skipping DB init (test/SQLite mode)")
    else:
        try:
            print("[STARTUP] Initializing database...")
            await init_db()

            print("[STARTUP] Setting up pgvector...")
            await setup_pgvector()
        except Exception as exc:
            # During tests/CI without Postgres, continue without startup DB init
            print(f"[STARTUP] DB init skipped due to error: {exc}")

    print("[STARTUP] Application ready!")

    yield

    # Shutdown
    print("[SHUTDOWN] Cleaning up...")


# Create FastAPI app
app = FastAPI(
    title="DocuChat API",
    description="Multi-tenant FastAPI backend with OpenAI RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics middleware
app.add_middleware(MetricsMiddleware)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    print(f"[ERROR] {type(exc).__name__}: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Include API routes
app.include_router(api_router)

# WebSocket route
app.websocket("/ws/chat")(websocket_chat_handler)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"name": "DocuChat API", "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
