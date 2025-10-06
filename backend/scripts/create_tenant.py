#!/usr/bin/env python3
"""Script to create a default tenant for testing"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker
from app.models.tenant import Tenant


async def create_default_tenant():
    """Create default tenant if it doesn't exist"""
    async with async_session_maker() as session:
        # Check if default tenant exists
        from sqlalchemy import select
        result = await session.execute(
            select(Tenant).where(Tenant.name == "default")
        )
        tenant = result.scalar_one_or_none()
        
        if tenant:
            print(f"✅ Default tenant already exists (ID: {tenant.id})")
            return tenant.id
        
        # Create default tenant
        tenant = Tenant(name="default")
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        
        print(f"✅ Created default tenant (ID: {tenant.id})")
        return tenant.id


if __name__ == "__main__":
    asyncio.run(create_default_tenant())
