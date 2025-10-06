"""Pytest configuration and fixtures"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.db.session import get_session
from app.core.config import get_settings

settings = get_settings()

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://docuchat:docuchat_pass@localhost:5432/docuchat_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session"""
    async with test_engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with test_session_maker() as session:
        yield session
        await session.rollback()
    
    # Clean up tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide a test HTTP client"""
    
    async def override_get_session():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def tenant_id() -> int:
    """Default tenant ID for tests"""
    return 1


@pytest.fixture
def tenant_headers(tenant_id: int) -> dict:
    """Default headers with tenant ID"""
    return {settings.TENANT_HEADER: str(tenant_id)}
