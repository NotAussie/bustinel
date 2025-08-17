"""This module defines the event model for trip creation events in the application."""

from bubus import BaseEvent
from pydantic import BaseModel

from models.beanie import Record
from models.tortoise import Agencies, Routes


class VehicleMeta(BaseModel):
    """Represents metadata for a vehicle event."""

    agency: Agencies
    route: Routes

    class Config:
        arbitrary_types_allowed = True


class TripCreatedEvent(BaseEvent):
    """Event triggered when a new trip is created."""

    record: Record
    meta: VehicleMeta
