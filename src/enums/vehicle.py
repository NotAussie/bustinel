"""This module defines vehicle-related enumerations for the application."""

from enum import IntEnum


class VehicleType(IntEnum):
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
