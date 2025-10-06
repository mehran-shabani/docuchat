"""Application configuration and settings"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/docuchat"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Allowed OpenAI models
    ALLOWED_MODELS: List[str] = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
    ]

    # Frontend
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    # Security
    JWT_SECRET: str = "change_me_to_a_random_secret_key_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 50

    # Multi-tenancy
    TENANT_HEADER: str = "X-Tenant-ID"

    # RAG Configuration
    CHUNK_TOKEN_SIZE: int = 400
    CHUNK_OVERLAP: int = 40
    MAX_CONTEXT_TOKENS: int = 8000
    TOP_K: int = 6

    # File upload limits
    MAX_FILE_SIZE_MB: int = 25
    MAX_PDF_PAGES: int = 500

    # Email verification code
    VERIFICATION_CODE_LENGTH: int = 6
    VERIFICATION_CODE_TTL_SECONDS: int = 600  # 10 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
