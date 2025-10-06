"""Tests for file upload endpoint"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

from app.models.tenant import Tenant
from app.models.user import User
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_upload_pdf_unauthorized(
    client: AsyncClient,
    tenant_headers: dict
):
    """Test upload without authentication"""
    response = await client.post(
        "/v1/files",
        headers=tenant_headers
    )
    
    # Should return 403 (missing auth) or 422 (missing file)
    assert response.status_code in [403, 422]


@pytest.mark.asyncio
async def test_upload_invalid_file_type(
    client: AsyncClient,
    db_session: AsyncSession,
    tenant_headers: dict
):
    """Test upload with non-PDF file"""
    # Create tenant and user
    tenant = Tenant(id=1, name="test")
    db_session.add(tenant)
    await db_session.commit()
    
    user = User(id=1, email="test@example.com", tenant_id=1)
    db_session.add(user)
    await db_session.commit()
    
    # Create token
    token = create_access_token({"sub": 1, "tenant_id": 1})
    
    # Try to upload non-PDF
    files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
    headers = {
        **tenant_headers,
        "Authorization": f"Bearer {token}"
    }
    
    response = await client.post(
        "/v1/files",
        files=files,
        headers=headers
    )
    
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]
