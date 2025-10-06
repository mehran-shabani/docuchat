"""API dependencies for authentication and tenant resolution"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.core.security import verify_token
from app.core.config import get_settings
from app.models.tenant import Tenant
from app.models.user import User

settings = get_settings()
security = HTTPBearer()


async def get_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias=settings.TENANT_HEADER)
) -> int:
    """
    Extract and validate tenant ID from header
    
    Args:
        x_tenant_id: Tenant ID from header
    
    Returns:
        Tenant ID as integer
    
    Raises:
        HTTPException: If tenant header is missing or invalid
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing {settings.TENANT_HEADER} header"
        )
    
    try:
        tenant_id = int(x_tenant_id)
        return tenant_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid {settings.TENANT_HEADER} header"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
    request: Request = None
) -> dict:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        tenant_id: Tenant ID from header
        session: Database session
        request: FastAPI request (for rate limiting)
    
    Returns:
        Dictionary with user_id and tenant_id
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Verify JWT token
    payload = verify_token(credentials.credentials)
    
    user_id: int = payload.get("sub")
    token_tenant_id: int = payload.get("tenant_id")
    
    if not user_id or not token_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify tenant matches
    if token_tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant mismatch"
        )
    
    # Verify user exists
    result = await session.execute(
        select(User).where(User.id == user_id).where(User.tenant_id == tenant_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Set user_id in request state for rate limiting
    if request:
        request.state.user_id = user_id
    
    return {
        "user_id": user_id,
        "tenant_id": tenant_id
    }


async def get_tenant(
    tenant_id: int = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session)
) -> Tenant:
    """
    Get tenant by ID
    
    Args:
        tenant_id: Tenant ID
        session: Database session
    
    Returns:
        Tenant model
    
    Raises:
        HTTPException: If tenant not found
    """
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant
