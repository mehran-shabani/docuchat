"""Database initialization with pgvector extension and indexes"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine


async def setup_pgvector() -> None:
    """Setup pgvector extension and create indexes"""
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Create ivfflat index on chunks.embedding for faster similarity search
        # Note: Index is created after tables exist
        try:
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS chunks_embedding_idx
                ON chunks
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
        except Exception as e:
            # Index might already exist or table might not exist yet
            print(f"Index creation skipped: {e}")


async def create_default_tenant(session: AsyncSession) -> int:
    """
    Create a default tenant for testing

    Args:
        session: Database session

    Returns:
        Tenant ID
    """
    from app.models.tenant import Tenant

    # Check if default tenant exists
    result = await session.execute(
        text("SELECT id FROM tenants WHERE name = 'default' LIMIT 1")
    )
    tenant = result.first()

    if tenant:
        return tenant[0]

    # Create default tenant
    tenant = Tenant(name="default")
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)

    return tenant.id
