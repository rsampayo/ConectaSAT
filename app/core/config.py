"""Application settings configuration."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./dev.db", description="Database connection URL"
    )

    # Security
    SECRET_KEY: str = Field(
        default="supersecretkey123456789", description="Secret key for JWT"
    )
    ALGORITHM: str = Field(default="HS256", description="Algorithm for JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )

    # Admin credentials (for initial setup)
    ADMIN_USERNAME: Optional[str] = Field(default="admin", description="Admin username")
    ADMIN_PASSWORD: Optional[str] = Field(
        default="changeme", description="Admin password"
    )

    # Application
    PROJECT_NAME: str = Field(
        default="CFDI Verification API", description="Project name"
    )
    API_V1_STR: str = Field(default="", description="API version prefix")

    # Make model_config a class variable
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True
    )


# Create settings instance
settings = Settings()
