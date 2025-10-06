"""Usage and quota schemas"""

from pydantic import BaseModel


class UsageWindow(BaseModel):
    """Token usage for a time window"""

    tokens_in: int
    tokens_out: int


class UsageOut(BaseModel):
    """Response schema for usage statistics"""

    window_24h: UsageWindow
    window_7d: UsageWindow
