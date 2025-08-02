"""Configuration utilities for the bustinel project.

This module loads configuration values from environment variables and files.
It provides constants for MongoDB connection, feed URL, update interval,
and HTTP headers.

Raises:
    ValueError: If required environment variables are not set.
"""

import os
from pathlib import Path
import logging

_ENV = os.environ

_MONGODB_URL_TEMP = _ENV.get("MONGODB_URL")
if _MONGODB_URL_TEMP is None:
    raise ValueError("MONGODB_URL environment variable is not set.")
MONGODB_URL: str = _MONGODB_URL_TEMP
"""The MongoDB connection URL for the bustinel database."""

_FEED_URL_TEMP = _ENV.get("FEED_URL")
if _FEED_URL_TEMP is None:
    raise ValueError("FEED_URL environment variable is not set.")
FEED_URL: str = _FEED_URL_TEMP
"""The URL to the GTFS-RT feed for vehicle positions."""

_GOOGLE_TRANSIT_FILE_URL_TEMP = _ENV.get("GOOGLE_TRANSIT_FILE_URL")
if _GOOGLE_TRANSIT_FILE_URL_TEMP is None:
    raise ValueError("GOOGLE_TRANSIT_FILE_URL environment variable is not set.")
GOOGLE_TRANSIT_FILE_URL: str = _GOOGLE_TRANSIT_FILE_URL_TEMP
"""The URL to the Google Transit feed file."""

_FEED_UPDATE_INTERVAL_ENV = _ENV.get("FEED_UPDATE_INTERVAL")
FEED_UPDATE_INTERVAL: int = (
    int(_FEED_UPDATE_INTERVAL_ENV)
    if _FEED_UPDATE_INTERVAL_ENV is not None
    else 60
)
"""The interval in seconds to update the feed data (default: 60 seconds)."""

_CONTACT_EMAIL_TEMP = _ENV.get("CONTACT_EMAIL")
if _CONTACT_EMAIL_TEMP is None:
    raise ValueError(
        "CONTACT_EMAIL environment variable is not set.\n"
        "This must be a valid email box in case of complaints from transit agencies."
    )
CONTACT_EMAIL: str = _CONTACT_EMAIL_TEMP
"""The host's contact email address for complaints or inquiries."""

_HEADERS_PATH = Path("data") / "headers.txt"


def _load_headers(path: Path) -> dict[str, str]:
    """Read headers from file and return a mapping, or empty dict if missing."""
    try:
        with path.open("r", encoding="utf-8") as f:
            headers: dict[str, str] = {}
            for line in f:
                if ":" not in line:
                    continue
                key, val = line.split(":", 1)
                headers[key.strip()] = val.strip()
            return headers
    except (FileNotFoundError, OSError):
        return {}


_HEADERS: dict[str, str] = _load_headers(_HEADERS_PATH)

ACCEPT = _ENV.get(
    "ACCEPT", "application/x-google-protobuf, application/x-protobuf"
)
"""The Accept header to be used for making requests to GTFS Realtime feeds. (default: 'application/x-google-protobuf, application/x-protobuf')"""

_REQUIRED_HEADERS: dict[str, str] = {
    "User-Agent": (
        f"Bustinel <https://github.com/notaussie/bustinel>; contact: {CONTACT_EMAIL}"
    ),
    "From": CONTACT_EMAIL,
}


HEADERS: dict[str, str] = {**_HEADERS, **_REQUIRED_HEADERS}
"""HTTP headers to be used in every outbound request."""


SENTRY_DSN: str | None = _ENV.get("SENTRY_DSN", None)
"""Sentry DSN for error reporting. (default: None)"""

_SENTRY_TRACES_SAMPLE_RATE = _ENV.get("SENTRY_TRACES_SAMPLE_RATE", "0.5")
try:
    SENTRY_TRACES_SAMPLE_RATE: float = float(_SENTRY_TRACES_SAMPLE_RATE)
    """Sentry traces sample rate for performance monitoring. (default: 0.5)"""
    if not 0.0 <= SENTRY_TRACES_SAMPLE_RATE <= 1.0:
        raise ValueError("SENTRY_TRACES_SAMPLE_RATE must be between 0.0 and 1.")
except ValueError:
    raise ValueError(
        f"Invalid SENTRY_TRACES_SAMPLE_RATE value: {_SENTRY_TRACES_SAMPLE_RATE}. "
        "Must be a float between 0.0 and 1.0."
    ) from None

ENVIRONMENT: str = _ENV.get("ENVIRONMENT", "production")
"""The environment in which the application is running (e.g., 'production', 'development', 'testing')."""

if ENVIRONMENT not in ("production", "development", "testing"):
    raise ValueError(
        f"Invalid ENVIRONMENT value: {ENVIRONMENT}. "
        "Must be one of 'production', 'development', or 'testing'."
    )

_LOG_LEVEL: int = getattr(
    logging, _ENV.get("LOG_LEVEL", "INFO").upper(), logging.INFO
)

LOG_LEVEL: int = _LOG_LEVEL
"""Logging level for the application (default: 'INFO')."""
