"""Tests for usage statistics endpoint"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quota import Quota
from app.models.tenant import Tenant
from app.models.user import User


@pytest.mark.asyncio
async def test_get_usage_unauthorized(client: AsyncClient, tenant_headers: dict):
    """Test getting usage without authentication"""
    response = await client.get("/v1/usage", headers=tenant_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_usage_empty(
    authenticated_client: AsyncClient, db_session: AsyncSession, tenant_headers: dict
):
    """Test getting usage with no data"""
    # Create tenant and user
    tenant = Tenant(id=1, name="test")
    db_session.add(tenant)
    await db_session.commit()

    user = User(id=1, email="test@example.com", tenant_id=1)
    db_session.add(user)
    await db_session.commit()

    response = await authenticated_client.get("/v1/usage", headers=tenant_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["window_24h"]["tokens_in"] == 0
    assert data["window_24h"]["tokens_out"] == 0
    assert data["window_7d"]["tokens_in"] == 0
    assert data["window_7d"]["tokens_out"] == 0


@pytest.mark.asyncio
async def test_get_usage_with_data(
    authenticated_client: AsyncClient, db_session: AsyncSession, tenant_headers: dict
):
    """Test getting usage with some data"""
    # Create tenant and user
    tenant = Tenant(id=1, name="test")
    db_session.add(tenant)
    await db_session.commit()

    user = User(id=1, email="test@example.com", tenant_id=1)
    db_session.add(user)
    await db_session.commit()

    # Add quota data
    quota = Quota(tenant_id=1, user_id=1, tokens_in=100, tokens_out=200)
    db_session.add(quota)
    await db_session.commit()

    response = await authenticated_client.get("/v1/usage", headers=tenant_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["window_24h"]["tokens_in"] == 100
    assert data["window_24h"]["tokens_out"] == 200
