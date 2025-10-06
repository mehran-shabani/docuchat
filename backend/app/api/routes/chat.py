"""Chat demo route"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/demo")
async def chat_demo():
    """Simple demo endpoint for existence check"""
    return {"message": "chat demo"}
