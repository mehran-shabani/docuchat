"""Tenant model for multi-tenancy"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    """Tenant model - represents an organization or workspace"""

    __tablename__ = "tenants"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
