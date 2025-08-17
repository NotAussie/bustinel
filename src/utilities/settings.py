"""This utility provides application-wide setting management via Pydantic."""

from pydantic import field_serializer
from pydantic_settings import BaseSettings


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

    @field_serializer("ENVIRONMENT")
    def serialize_environment(self, value: str) -> str:
        """Serialize the environment setting."""
        if value not in ["production", "development", "testing"]:
            raise ValueError("Invalid environment value")

        return value.lower()
