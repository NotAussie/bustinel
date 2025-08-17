"""This module defines all Beanie ODM models."""

from .record import Agency, Record, Route, Trip, Vehicle

collections = [Record]

__all__ = [
    "Record",
    "Route",
    "Vehicle",
    "Trip",
    "Agency",
    "collections",
]
