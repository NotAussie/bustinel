"""This module defines the routes table model."""

from tortoise import Model, fields

from enums import VehicleType


class Routes(Model):
    """Represents a route from a GTFS feed.

    Attributes:
        route_id (str): Unique identifier for the route.
        agency_id (str): Identifier for the agency that operates the route.
        route_short_name (str | None): Short name of the route. (E.g. `401`)
        route_long_name (str | None): Long name of the route. (E.g. `Paralowie to Salisbury`)
        route_desc (str | None): Description of the route (optional).
        route_type (VehicleType): Type of vehicle used for the route.
    """

    route_id = fields.TextField(primary_key=True)
    agency_id = fields.TextField()
    route_short_name = fields.TextField(null=True)
    route_long_name = fields.TextField(null=True)
    route_desc = fields.TextField(null=True)
    route_type = fields.IntEnumField(VehicleType, default=VehicleType.UNKNOWN)

    class Meta:  # type: ignore
        table = "routes"
        unique_together = (("route_id", "agency_id"),)
