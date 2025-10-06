"""Rate limiting service using SlowAPI and Redis"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from app.core.config import get_settings

settings = get_settings()


def get_user_id_or_ip(request: Request) -> str:
    """
    Get user ID from request state or fall back to IP address
    
    Args:
        request: FastAPI request
    
    Returns:
        User identifier string
    """
    # Try to get user_id from request state (set by auth dependency)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_user_id_or_ip,
    storage_uri=settings.REDIS_URL,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)
