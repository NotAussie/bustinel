"""This module defines GTFS-RT protocol classes."""

from .gtfsr_proto import Alert, FeedMessage, TripUpdate, VehiclePosition

__all__ = [
    "FeedMessage",
    "Alert",
    "TripUpdate",
    "VehiclePosition",
]
