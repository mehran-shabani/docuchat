"""Chat schemas"""

from typing import Optional

from pydantic import BaseModel


class ChatIn(BaseModel):
    """Request schema for chat message"""

    message: str
    session_id: Optional[int] = None


class ChatOut(BaseModel):
    """Response schema for chat message"""

    response: str
    session_id: int
    tokens_in: int
    tokens_out: int
