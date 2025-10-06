"""Chat session and message models"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ChatSession(SQLModel, table=True):
    """ChatSession model - represents a chat conversation"""
    
    __tablename__ = "chat_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Message model - represents a single message in a chat session"""
    
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id", index=True)
    role: str = Field(max_length=50)  # 'user' or 'assistant'
    content: str
    tokens_in: int = Field(default=0)
    tokens_out: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
