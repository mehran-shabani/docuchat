"""Chunk model for document embeddings"""

from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, SQLModel


class Chunk(SQLModel, table=True):
    """Chunk model - represents a text chunk with embedding vector"""

    __tablename__ = "chunks"

    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    page: int
    text: str = Field(max_length=5000)
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(1536)))

    class Config:
        arbitrary_types_allowed = True
