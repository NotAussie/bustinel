"""This module defines the agencies table model."""

from tortoise import Model, fields


class Agencies(Model):
    """Represents an agency from a GTFS feed.

    Attributes:
        agency_id (str): Unique identifier for the agency.
        agency_name (str): Name of the agency.
        agency_url (str): URL of the agency's website.
        agency_timezone (str): Timezone of the agency. (In IANA format, e.g. `Australia/Adelaide`)
        agency_lang (str | None): Language of the agency (optional).
        agency_phone (str | None): Phone number of the agency (optional).
        agency_fare_url (str | None): URL for fare information (optional).
        agency_email (str | None): Email address for the agency (optional).
    """

    agency_id = fields.TextField(primary_key=True)
    agency_name = fields.TextField()
    agency_url = fields.TextField()
    agency_timezone = fields.TextField()
    agency_lang = fields.TextField(null=True)
    agency_phone = fields.TextField(null=True)
    agency_fare_url = fields.TextField(null=True)
    agency_email = fields.TextField(null=True)

    class Meta:  # type: ignore
        table = "agencies"
