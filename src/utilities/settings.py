"""This utility provides application-wide setting management via Pydantic."""

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Configuration settings for the application."""

    MONGODB_URI: str
    MONGODB_DATABASE: str = "bustinel"

    REDIS_URI: str = "redis://localhost:6379/0"
    REDIS_PREFIX: str = "bustinel"

    METADATA_URL: str
    FEED_URL: str

    METADATA_REFRESH_INTERVAL: int = 3600

    FEED_REFRESH_INTERVAL: int = 300

    ENVIRONMENT: str = "production"

    @field_validator("ENVIRONMENT", mode="before")
    def validate_environment(self, value: str) -> str:
        """Validate and normalize the environment setting."""
        value = value.lower()
        if value not in ["production", "development", "testing"]:
            raise ValueError("Invalid environment value")
        return value
