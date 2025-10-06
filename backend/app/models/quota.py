"""Quota and usage tracking model"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Quota(SQLModel, table=True):
    """Quota model - tracks token usage per tenant/user"""
    
    __tablename__ = "quotas"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    tokens_in: int = Field(default=0)
    tokens_out: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
