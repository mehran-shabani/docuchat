"""File upload schemas"""

from pydantic import BaseModel


class UploadOut(BaseModel):
    """Response schema for file upload"""

    document_id: int
    chunks: int
    elapsed_ms: float
