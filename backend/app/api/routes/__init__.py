"""API routes"""

from fastapi import APIRouter

from app.api.routes import auth, files, health, usage
from app.api.routes import chat

api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(files.router, prefix="/v1/files", tags=["files"])
api_router.include_router(usage.router, prefix="/v1/usage", tags=["usage"])
api_router.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
