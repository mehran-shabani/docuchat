"""Authentication routes"""

import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from app.db.session import get_session
from app.api.deps import get_tenant_id
from app.schemas.auth import EmailRequestIn, VerifyCodeIn, TokenOut
from app.core.security import create_access_token
from app.core.config import get_settings
from app.models.user import User

settings = get_settings()
router = APIRouter()

# Redis client for verification codes
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.post("/request-code", status_code=status.HTTP_200_OK)
async def request_verification_code(
    data: EmailRequestIn,
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Request a verification code for email
    
    Sends a 6-digit code to the user's email (currently logged for PoC)
    """
    # Generate 6-digit code
    code = "".join([str(random.randint(0, 9)) for _ in range(settings.VERIFICATION_CODE_LENGTH)])
    
    # Store in Redis with TTL
    key = f"{tenant_id}:{data.email}"
    await redis_client.setex(
        key,
        settings.VERIFICATION_CODE_TTL_SECONDS,
        code
    )
    
    # TODO: Send email in production
    # For PoC, just log it
    print(f"[AUTH] Verification code for {data.email}: {code}")
    
    return {"message": "Verification code sent"}


@router.post("/verify-code", response_model=TokenOut)
async def verify_code(
    data: VerifyCodeIn,
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Verify code and issue JWT token
    
    Creates user if doesn't exist and returns access token
    """
    # Check code in Redis
    key = f"{tenant_id}:{data.email}"
    stored_code = await redis_client.get(key)
    
    if not stored_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired or not found"
        )
    
    if stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Delete code from Redis (one-time use)
    await redis_client.delete(key)
    
    # Find or create user
    result = await session.execute(
        select(User)
        .where(User.email == data.email)
        .where(User.tenant_id == tenant_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            email=data.email,
            tenant_id=tenant_id
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # Create JWT token
    token_data = {
        "sub": user.id,
        "tenant_id": tenant_id,
        "email": user.email
    }
    access_token = create_access_token(token_data)
    
    return TokenOut(access_token=access_token)
