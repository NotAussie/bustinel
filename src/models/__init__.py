"""
This module initializes and exposes core data models for the application.

It imports and makes available the primary model classes, such as Record, Vehicle, Trip, Agency, and VehicleType,
which are used throughout the project for representing and managing vehicle entities.
"""

from .record import Record, Vehicle, Trip, Agency, VehicleType

__models = [Record]
