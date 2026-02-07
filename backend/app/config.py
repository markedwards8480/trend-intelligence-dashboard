from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings using pydantic-settings."""

    # App metadata
    APP_NAME: str = "Trend Intelligence Dashboard"
    APP_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/trend_dashboard"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API Keys
    CLAUDE_API_KEY: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    SENDGRID_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Feature flags
    USE_MOCK_AI: bool = True

    # AWS S3
    AWS_S3_BUCKET: str = "trend-intelligence-assets"
    AWS_REGION: str = "us-east-1"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
