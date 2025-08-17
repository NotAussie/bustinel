"""This module defines the RealtimeService class, which is responsible for processing GTFS-RT feeds."""

import asyncio
from datetime import datetime
from hashlib import sha3_256

import logfire
import sentry_sdk
from aiohttp import ClientSession
from bubus import EventBus
from redis.asyncio import Redis

from models.beanie import Agency, Record, Route, Trip, Vehicle
from models.events import TripCreatedEvent, VehicleMeta
from models.tortoise import Agencies, Routes
from proto import FeedMessage, VehiclePosition
from utilities import ServiceBase, Settings, pcall


class RealtimeService(ServiceBase):
    """Service for generating realtime events based on GTFS vehicles."""

    def __init__(self, bus: EventBus, redis: Redis):
        super().__init__(bus, redis)

        self.first_run = True

    def _serialise_vehicle(
        self, trip: Trip, agency: Agency, vehicle: Vehicle
    ) -> str:
        """Serialises a vehicle into a unique hash based on its details."""

        return sha3_256(
            f"{trip.id}:{agency.id}:{vehicle.id}:{vehicle.label}".encode(
                "utf-8"
            )
        ).hexdigest()

    async def _process_vehicles(self, vehicles: list[VehiclePosition]) -> None:
        """
        Processes a list of VehiclePosition objects, performing the following steps for each vehicle:

                Args:
            vehicles (list[VehiclePosition]): A list of VehiclePosition objects to process.
        Returns:
            None
        """

        inserts = []
        events = []

        for vehicle in vehicles:
            route = await Routes.get_or_none(
                route_id=vehicle.trip.route_id,
            )
            if not route:
                self.logger.warning(
                    "Route not found for vehicle",
                    extra={
                        "vehicle_id": vehicle.vehicle.id,
                        "route_id": vehicle.trip.route_id,
                    },
                )
                continue

            agency = await Agencies.get_or_none(agency_id=route.agency_id)
            if not agency:
                self.logger.warning(
                    "Agency not found for vehicle",
                    extra={
                        "vehicle_id": vehicle.vehicle.id,
                        "agency_id": route.agency_id,
                    },
                )
                continue

            record = Record(
                vehicle=Vehicle(
                    id=vehicle.vehicle.id,
                    plate=(
                        vehicle.vehicle.license_plate
                        if vehicle.vehicle.license_plate
                        and len(vehicle.vehicle.license_plate) > 1
                        else None
                    ),
                    label=(
                        vehicle.vehicle.label
                        if vehicle.vehicle.label
                        and len(vehicle.vehicle.label) > 0
                        else None
                    ),
                    type=route.route_type,
                ),
                trip=Trip(
                    id=vehicle.trip.trip_id,
                    direction=vehicle.trip.direction_id,
                    route=Route(
                        id=route.route_id,
                        short_name=route.route_short_name,
                        long_name=route.route_long_name,
                        type=route.route_type,
                    ),
                ),
                agency=Agency(
                    id=agency.agency_id,
                    name=agency.agency_name,
                    url=agency.agency_url,
                    timezone=agency.agency_timezone,
                ),
                timestamp=datetime.fromtimestamp(vehicle.timestamp),
            )

            self.logger.debug(
                "Processing trip", extra={"record": record.model_dump()}
            )

            serialised = self._serialise_vehicle(
                record.trip, record.agency, record.vehicle
            )
            cached = await self.redis.exists(
                f"{Settings.REDIS_PREFIX}:vehicle:{serialised}"
            )
            if cached:
                self.logger.debug(
                    "Vehicle already processed, skipping",
                    extra={
                        "serialised": serialised,
                        "record": record.model_dump(),
                    },
                )
                continue

            exists = await Record.find_one(
                {
                    "trip.id": record.trip.id,
                    "agency.name": record.agency.name,
                    "agency.id": record.agency.id,
                    "vehicle.id": record.vehicle.id,
                }
            )
            if exists:
                self.logger.warning(
                    "Vehicle prematurely disposed, re-caching",
                    extra={
                        "serialised": serialised,
                        "record": record.model_dump(),
                    },
                )
                await self.redis.set(
                    f"{Settings.REDIS_PREFIX}:vehicle:{serialised}",
                    "1",
                    ex=60 * 60 * 24,
                )
                continue

            inserts.append(record)
            events.append(
                TripCreatedEvent(
                    record=record,
                    meta=VehicleMeta(agency=agency, route=route),
                )
            )

            self.logger.info(
                "New trip created",
                extra={
                    "serialised": serialised,
                    "record": record.model_dump(),
                },
            )

        if inserts:
            await Record.insert_many(inserts)
        for event in events:
            self.bus.dispatch(event)

    async def runner(self):
        """Periodically fetches GTFS-RT data, saves it to the database, and publishes any new vehicle."""
        while not self._stop.is_set():

            if not self.first_run:
                await asyncio.sleep(Settings.FEED_REFRESH_INTERVAL)

            with sentry_sdk.start_transaction(name=self.logger.name):
                with logfire.span("Polling GTFS-RT feed"):
                    async with ClientSession() as session:

                        response, success = await pcall(
                            session.get(Settings.FEED_URL)
                        )
                        if not success and isinstance(response, Exception):
                            self.logger.error(
                                "Failed to fetch GTFS-RT feed",
                                exc_info=response,
                                extra={"feed_url": Settings.FEED_URL},
                            )
                            continue

                        assert not isinstance(  # nosec bandit
                            response, BaseException
                        ), "Response should not be an exception"

                        response.raise_for_status()

                        message = FeedMessage()
                        message.ParseFromString(await response.read())

                        vehicles = [
                            entity.vehicle
                            for entity in message.entity
                            if entity.HasField("vehicle")
                        ]

                        err, success = await pcall(
                            self._process_vehicles(vehicles)
                        )
                        if not success:
                            self.logger.error(
                                "Failed to process vehicles",
                                extra={
                                    "feed_url": Settings.FEED_URL,
                                    "vehicles_count": len(vehicles),
                                },
                                exc_info=err,
                            )
                            continue

            self.first_run = False


def mount(bus: EventBus, redis: Redis) -> RealtimeService:
    """
    Mounts the RealtimeService to the provided EventBus and Redis instance.

    Args:
        bus (EventBus): The event bus to which the service will be mounted.
        redis (Redis): The Redis instance for caching and data storage.

    Returns:
        RealtimeService: An instance of the RealtimeService.
    """
    return RealtimeService(bus, redis)
