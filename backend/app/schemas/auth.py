"""Authentication schemas"""

from pydantic import BaseModel, EmailStr


class EmailRequestIn(BaseModel):
    """Request schema for email verification code"""
    email: EmailStr


class VerifyCodeIn(BaseModel):
    """Request schema for code verification"""
    email: EmailStr
    code: str


class TokenOut(BaseModel):
    """Response schema for JWT token"""
    access_token: str
    token_type: str = "bearer"
