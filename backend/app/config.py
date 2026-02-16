from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """Application settings using pydantic-settings."""

    # App metadata
    APP_NAME: str = "Trend Intelligence Dashboard"
    APP_VERSION: str = "1.0.0"

    # Database - defaults to SQLite for easy local dev
    DATABASE_URL: str = "sqlite:///./trend_dashboard.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API Keys
    CLAUDE_API_KEY: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    SENDGRID_API_KEY: str = ""

    # CORS - accepts "*" or comma-separated origins
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://trend-intelligence-dashboard-production.up.railway.app"

    # Feature flags
    USE_MOCK_AI: bool = True

    # Scraping
    APIFY_TOKEN: str = ""
    X_API_BEARER_TOKEN: str = ""

    # AWS S3
    AWS_S3_BUCKET: str = "trend-intelligence-assets"
    AWS_REGION: str = "us-east-1"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
