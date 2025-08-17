"""
This module defines data models for representing historical records of vehicle trips,
including trip details, vehicle information, agency data, and associated metadata.
"""

from datetime import datetime

from beanie import Document
from pydantic import BaseModel

from enums import VehicleType


class Route(BaseModel):
    """
    Represents a route record.

    Attributes:
        id (str): Unique identifier for the route.
        name (str): Name of the route.
        route_short_name (str): Short name of the route. (E.g. `401`)
        route_long_name (str | None): Long name of the route. (E.g. `Paralowie to Salisbury`)
        route_type (VehicleType): Type of vehicle used for the route.
    """

    id: str
    short_name: str
    long_name: str | None = None
    type: VehicleType = VehicleType.UNKNOWN


class Trip(BaseModel):
    """
    Represents a trip record.

    Attributes:
        id (str): Unique identifier for the trip.
        direction (int): Direction of the trip.
        route (Route): Route identifier.
    """

    id: str
    direction: int
    route: Route


class Vehicle(BaseModel):
    """
    Represents a vehicle record.

    Attributes:
        id (str): Unique identifier for the vehicle.
        plate (str | None): License plate number of the vehicle, or None if not assigned.
        type (int): Integer representing the type of vehicle.
    """

    id: str
    label: str | None
    plate: str | None
    type: VehicleType = VehicleType.UNKNOWN


class Agency(BaseModel):
    """
    Represents an agency.

    Attributes:
        id (str): Unique identifier for the agency.
        name (str): Name of the agency.
        url (str): URL of the agency's website.
        timezone (str): Timezone of the agency. (In IANA format, e.g. `Australia/Adelaide`)
    """

    id: str
    name: str
    url: str
    timezone: str


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
