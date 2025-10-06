"""Document model for uploaded PDFs"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Document(SQLModel, table=True):
    """Document model - represents an uploaded PDF file"""

    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    title: str = Field(max_length=500)
    pages: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
