"""
This module defines data models for representing historical records of vehicle trips,
including trip details, vehicle information, agency data, and associated metadata.
"""

from datetime import datetime
from enum import Enum
from beanie import Document
from pydantic import BaseModel


class Trip(BaseModel):
    """
    Represents a trip record.

    Attributes:
        id (str): Unique identifier for the trip.
        direction (int): Direction of the trip.
        route (str): Route identifier.
    """

    id: str
    direction: int
    route: str


class VehicleType(Enum):
    """
    Enum representing different types of vehicles.

    Attributes:
        TRAM (0): Tram, Streetcar, Light rail.
        SUBWAY (1): Subway, Metro, Underground.
        RAIL (2): Rail, Long-distance train, Intercity, Regional.
        BUS (3): Bus, Coach, Transit bus.
        FERRY (4): Ferry, Water transport.
        CABLE_TRAM (5): Cable tram.
        AERIAL_LIFT (6): Aerial lift, Gondola, Suspended cable car.
        FUNICULAR (7): Funicular railway.
        TROLLEYBUS (11): Trolleybus.
        MONORAIL (12): Monorail.
        UNKNOWN (1000): Unknown or unspecified vehicle type.
    """

    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_TRAM = 5
    AERIAL_LIFT = 6
    FUNICULAR = 7
    TROLLEYBUS = 11
    MONORAIL = 12

    UNKNOWN = 1000


class Vehicle(BaseModel):
    """
    Represents a vehicle record.

    Attributes:
        id (str): Unique identifier for the vehicle.
        plate (str | None): License plate number of the vehicle, or None if not assigned.
        type (int): Integer representing the type of vehicle.
    """

    id: str
    label: str | None = None
    plate: str | None
    type: VehicleType = VehicleType.UNKNOWN


class Agency(BaseModel):
    """
    Represents an agency.

    Attributes:
        id (str): Unique identifier for the agency.
        name (str): Name of the agency.
    """

    id: str
    name: str
    url: str


class Record(Document):
    """
    Represents a historical record of a vehicle trip for statistical purposes.

    Attributes:
        vehicle (Vehicle): Vehicle information for the record.
        trip (Trip): Trip information for the record.
        agency (Agency): Agency information for the record.
        timestamp (datetime): Timestamp of the record.
    """

    vehicle: Vehicle

    trip: Trip

    agency: Agency

    timestamp: datetime

    class Settings:
        name = "records"
