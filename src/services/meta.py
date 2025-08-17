"""This module defines the MetaService class for managing GTFS metadata updates."""

import asyncio
import csv
import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO

import aiohttp
import logfire
import sentry_sdk
from bubus import EventBus
from redis.asyncio import Redis

from enums import VehicleType
from models.tortoise import Agencies, Routes
from utilities import ServiceBase, Settings, pcall


class MetaService(ServiceBase):
    """Service for automatically refreshing GTFS metadata."""

    def __init__(self, bus: EventBus, redis: Redis):
        super().__init__(bus, redis)

        self.first_run = True
        self.last_modified = (
            datetime.now(timezone.utc) - timedelta(days=30)
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")

    async def _load_agencies(self, data: bytes) -> None:

        reader = csv.DictReader(data.decode("utf-8").splitlines())
        rows = list(reader)

        for row in rows:
            with sentry_sdk.start_span(op="cache.put") as span:

                agency_id = row.get("agency_id")
                if len(rows) <= 1 and not agency_id:
                    # NOTE: This is required by GTFS specification, though due to limitations we must provide an internal default.
                    self.logger.warning(
                        "No agencies found in the data, using default agency_id",
                    )
                    agency_id = "default"

                if not agency_id:
                    self.logger.error(
                        "Agency ID is missing, skipping row",
                        extra={"row": row},
                    )
                    continue

                agency_name = row.get("agency_name")
                if not agency_name:
                    self.logger.error(
                        "Agency name is missing, skipping row",
                        extra={"row": row},
                    )
                    continue

                agency_url = row.get("agency_url")
                if not agency_url:
                    self.logger.error(
                        "Agency URL is missing, skipping row",
                        extra={"row": row},
                    )
                    continue

                agency_timezone = row.get("agency_timezone")
                if not agency_timezone:
                    self.logger.error(
                        "Agency timezone is missing, skipping row",
                        extra={"row": row},
                    )
                    continue

                agency_lang = row.get("agency_lang")
                agency_phone = row.get("agency_phone")
                agency_fare_url = row.get("agency_fare_url")
                agency_email = row.get("agency_email")

                span.set_data(
                    "cache.key",
                    [f"{Agencies.Meta.table}:{agency_id}"],
                )

                result = await Agencies.update_or_create(
                    agency_id=agency_id,
                    defaults={
                        "agency_name": agency_name,
                        "agency_url": agency_url,
                        "agency_timezone": agency_timezone,
                        "agency_lang": agency_lang,
                        "agency_phone": agency_phone,
                        "agency_fare_url": agency_fare_url,
                        "agency_email": agency_email,
                    },
                )

                self.logger.debug(
                    "Set agency %s",
                    result[0].agency_id,
                    extra={"agency_id": result[0].agency_id},
                )

    async def _load_routes(self, data: bytes) -> None:
        reader = csv.DictReader(data.decode("utf-8").splitlines())
        rows = list(reader)

        for row in rows:
            with sentry_sdk.start_span(op="cache.put") as span:

                route_id = row.get("route_id")
                if not route_id:
                    self.logger.error(
                        "Route ID is missing, skipping row",
                        extra={"row": row},
                    )
                    continue

                agency_id = row.get("agency_id")
                if not agency_id:
                    agency_count = await Agencies.all().count()
                    if agency_count <= 1:
                        # NOTE: This is required by GTFS specification, though due to limitations we must provide an internal default.
                        self.logger.debug(
                            "No agencies found in the data, using default agency_id",
                        )
                        agency_id = "default"

                route_short_name = row.get("route_short_name")
                route_long_name = row.get("route_long_name")
                route_desc = row.get("route_desc")
                route_type = VehicleType(int(row.get("route_type", 1000)))

                span.set_data(
                    "cache.key",
                    [f"{Routes.Meta.table}:{route_id}:{agency_id}"],
                )

                result = await Routes.update_or_create(
                    route_id=route_id,
                    agency_id=agency_id,
                    defaults={
                        "route_short_name": route_short_name,
                        "route_long_name": route_long_name,
                        "route_desc": route_desc,
                        "route_type": route_type,
                    },
                )

                self.logger.debug(
                    "Set route %s for agency %s",
                    result[0].route_id,
                    result[0].agency_id,
                    extra={
                        "route_id": result[0].route_id,
                        "agency_id": result[0].agency_id,
                    },
                )

    async def runner(self):
        """
        Periodically fetches and updates GTFS metadata from a remote feed.

        Raises:
            AssertionError: If the HTTP response is an exception.
            Exception: Propagates exceptions encountered during route update/create operations.
        """

        while not self._stop.is_set():
            if not self.first_run:
                await asyncio.sleep(Settings.METADATA_REFRESH_INTERVAL)

            with sentry_sdk.start_transaction(name=self.logger.name):
                with logfire.span("Refreshing GTFS metadata"):
                    async with aiohttp.ClientSession() as session:
                        response, success = await pcall(
                            session.get(
                                Settings.METADATA_URL,
                                headers={
                                    "If-Modified-Since": self.last_modified
                                },
                            )
                        )
                        if not success and isinstance(response, Exception):
                            self.logger.error(
                                "Failed to fetch metadata",
                                exc_info=response,
                                extra={
                                    "feed_metadata_url": Settings.METADATA_URL
                                },
                            )
                            sentry_sdk.capture_exception(response)
                            continue

                        assert not isinstance(  # nosec bandit
                            response, BaseException
                        ), "Response should not be an exception"

                        response.raise_for_status()

                        if response.status == 304:
                            self.logger.info(
                                "Metadata not modified, skipping update",
                                extra={"last_modified": self.last_modified},
                            )
                            continue

                        self.last_modified = response.headers.get(
                            "Last-Modified", self.last_modified
                        )

                        self.logger.info(
                            "Metadata updated, processing new data",
                            extra={
                                "last_modified": self.last_modified,
                                "feed_metadata_url": Settings.METADATA_URL,
                            },
                        )

                        data = BytesIO(await response.read())  # Zip file
                        with zipfile.ZipFile(data, "r") as zf:

                            with sentry_sdk.start_span(
                                name="Load agencies",
                                op="load.agencies",
                            ):
                                with logfire.span("Load agencies"):
                                    agency = zf.read("agency.txt")
                                    await self._load_agencies(agency)

                            with sentry_sdk.start_span(
                                name="Load routes",
                                op="load.routes",
                            ):
                                with logfire.span("Load routes"):
                                    routes = zf.read("routes.txt")
                                    await self._load_routes(routes)

            self.first_run = False


def mount(bus: EventBus, redis: Redis) -> MetaService:
    """
    Mounts the MetaService to the provided EventBus and Redis instance.

    Args:
        bus (EventBus): The event bus to which the service will be mounted.
        redis (Redis): The Redis instance for caching and data storage.

    Returns:
        MetaService: An instance of the MetaService.
    """
    return MetaService(bus, redis)
