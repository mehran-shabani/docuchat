"""Token usage metering service"""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quota import Quota


async def record_token_usage(
    session: AsyncSession, tenant_id: int, user_id: int, tokens_in: int, tokens_out: int
) -> None:
    """
    Record token usage in quota table

    Args:
        session: Database session
        tenant_id: Tenant ID
        user_id: User ID
        tokens_in: Input tokens count
        tokens_out: Output tokens count
    """
    quota = Quota(
        tenant_id=tenant_id,
        user_id=user_id,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        timestamp=datetime.utcnow(),
    )

    session.add(quota)
    await session.commit()


async def get_usage_stats(session: AsyncSession, tenant_id: int, user_id: int) -> dict:
    """
    Get usage statistics for a user

    Args:
        session: Database session
        tenant_id: Tenant ID
        user_id: User ID

    Returns:
        Dictionary with usage stats for 24h and 7d windows
    """
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    # Query for 24h window
    result_24h = await session.execute(
        select(
            func.sum(Quota.tokens_in).label("tokens_in"),
            func.sum(Quota.tokens_out).label("tokens_out"),
        )
        .where(Quota.tenant_id == tenant_id)
        .where(Quota.user_id == user_id)
        .where(Quota.timestamp >= day_ago)
    )

    row_24h = result_24h.first()

    # Query for 7d window
    result_7d = await session.execute(
        select(
            func.sum(Quota.tokens_in).label("tokens_in"),
            func.sum(Quota.tokens_out).label("tokens_out"),
        )
        .where(Quota.tenant_id == tenant_id)
        .where(Quota.user_id == user_id)
        .where(Quota.timestamp >= week_ago)
    )

    row_7d = result_7d.first()

    return {
        "window_24h": {"tokens_in": row_24h[0] or 0, "tokens_out": row_24h[1] or 0},
        "window_7d": {"tokens_in": row_7d[0] or 0, "tokens_out": row_7d[1] or 0},
    }
