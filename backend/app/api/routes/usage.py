"""Usage statistics routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.schemas.usage import UsageOut, UsageWindow
from app.services.tokens_meter import get_usage_stats

router = APIRouter()


@router.get("", response_model=UsageOut)
async def get_usage(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get token usage statistics for current user

    Returns usage for 24h and 7d windows
    """
    stats = await get_usage_stats(
        session,
        current_user["tenant_id"],
        current_user["user_id"]
    )
    
    return UsageOut(
        window_24h=UsageWindow(**stats["window_24h"]),
        window_7d=UsageWindow(**stats["window_7d"])
    )
