"""This module defines all utility functions and classes."""

from .pcall import pcall
from .service import ServiceBase
from .settings import Settings as _Settings

Settings = _Settings()  # type: ignore
