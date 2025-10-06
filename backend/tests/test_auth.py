"""Tests for authentication endpoints"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.models.tenant import Tenant
from app.core.config import get_settings

settings = get_settings()


@pytest.mark.asyncio
async def test_request_code(
    client: AsyncClient,
    db_session: AsyncSession,
    tenant_headers: dict
):
    """Test requesting verification code"""
    # Create tenant first
    tenant = Tenant(id=1, name="test")
    db_session.add(tenant)
    await db_session.commit()
    
    response = await client.post(
        "/v1/auth/request-code",
        json={"email": "test@example.com"},
        headers=tenant_headers
    )
    
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_verify_code_invalid(
    client: AsyncClient,
    db_session: AsyncSession,
    tenant_headers: dict
):
    """Test verifying invalid code"""
    # Create tenant
    tenant = Tenant(id=1, name="test")
    db_session.add(tenant)
    await db_session.commit()
    
    response = await client.post(
        "/v1/auth/verify-code",
        json={"email": "test@example.com", "code": "000000"},
        headers=tenant_headers
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_auth_flow(
    client: AsyncClient,
    db_session: AsyncSession,
    tenant_headers: dict
):
    """Test complete authentication flow"""
    # Create tenant
    tenant = Tenant(id=1, name="test")
    db_session.add(tenant)
    await db_session.commit()
    
    email = "user@example.com"
    
    # Request code
    await client.post(
        "/v1/auth/request-code",
        json={"email": email},
        headers=tenant_headers
    )
    
    # Get code from Redis
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    code = await redis_client.get(f"1:{email}")
    
    assert code is not None
    
    # Verify code
    response = await client.post(
        "/v1/auth/verify-code",
        json={"email": email, "code": code},
        headers=tenant_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    await redis_client.close()
