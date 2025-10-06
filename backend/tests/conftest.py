"""Pytest configuration and fixtures"""

from typing import AsyncGenerator
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Ensure app startup DB init is disabled before app import
os.environ.setdefault("DISABLE_STARTUP_INIT", "1")

from app.core.config import get_settings
from app.db.session import get_session
from app.main import app

settings = get_settings()

# Test database URL (use SQLite for CI/tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
test_session_maker = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Provide a simple in-memory fake Redis for tests."""
    # Ensure app startup does not hit Postgres/pgvector during tests
    monkeypatch.setenv("DISABLE_STARTUP_INIT", "1")

    from app.api.routes import auth as auth_module
    import redis.asyncio as redis_module

    shared_store: dict[str, str] = {}

    class FakeRedis:
        def __init__(self):
            # Share storage across all instances
            self._store = shared_store

        async def setex(self, key: str, ttl_seconds: int, value: str):
            self._store[key] = value

        async def get(self, key: str):
            return self._store.get(key)

        async def delete(self, key: str):
            self._store.pop(key, None)

        async def close(self):
            return None

    # Single shared instance for module-level client and any from_url() calls
    fake_instance = FakeRedis()
    # Replace global client in auth module
    monkeypatch.setattr(auth_module, "redis_client", fake_instance)
    # Replace factory so tests creating their own client get the same fake instance
    monkeypatch.setattr(redis_module, "from_url", lambda *args, **kwargs: fake_instance)
    yield


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session"""
    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.document import Document
    from app.models.quota import Quota

    async with test_engine.begin() as conn:
        # Only attempt pgvector extension on PostgreSQL
        if TEST_DATABASE_URL.startswith("postgresql"):
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        def _create_all(connection):
            SQLModel.metadata.create_all(
                bind=connection,
                tables=[
                    Tenant.__table__,
                    User.__table__,
                    Document.__table__,
                    Quota.__table__,
                ],
            )

        # Create required tables only (avoid pgvector-dependent tables on SQLite)
        await conn.run_sync(_create_all)

    async with test_session_maker() as session:
        yield session
        await session.rollback()

    # Clean up only the created tables after test
    async with test_engine.begin() as conn:
        def _drop_all(connection):
            SQLModel.metadata.drop_all(
                bind=connection,
                tables=[
                    Tenant.__table__,
                    User.__table__,
                    Document.__table__,
                    Quota.__table__,
                ],
            )

        await conn.run_sync(_drop_all)


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
