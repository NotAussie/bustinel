"""
This module provides asynchronous routines for fetching, processing, and recording GTFS-RT (General Transit Feed Specification Realtime) vehicle position data. It periodically retrieves vehicle positions from a configured GTFS-RT feed, matches them with route and agency information, and stores new vehicle trip records in the database. The module is designed to run continuously, handling errors gracefully and supporting concurrent processing of multiple vehicle positions.

Typical usage involves running the `run_recorder` coroutine, which manages the entire data collection and recording workflow.
"""

import csv
import asyncio
import logging
from datetime import datetime
from aiohttp import ClientSession

from models import Record, Trip, Vehicle, VehicleType, Agency
from utils import GTFSRT, transit, config

logger = logging.getLogger(__name__)


async def process_vehicle(
    vehicle,
    routes: list[list[str]],
    agencies: list[list[str]],
) -> None:
    """Processes a single GTFS-RT vehicle position."""
    route = next((r for r in routes if r[0] == vehicle.trip.route_id), None)
    if not route:
        logger.warning(
            "route not found for vehicle",
            extra={
                "vehicle_id": vehicle.vehicle.id,
                "route_id": vehicle.trip.route_id,
            },
        )
        return

    agency = next((a for a in agencies if a[0] == route[1]), None)
    if not agency:
        logger.warning(
            "agency not found for vehicle",
            extra={
                "vehicle_id": vehicle.vehicle.id,
                "agency_id": route[1],
            },
        )
        return

    vehicle_type = int(route[5]) if len(route) > 5 and route[5] else 1000
    license_plate = (
        vehicle.vehicle.license_plate
        if vehicle.vehicle.license_plate
        and len(vehicle.vehicle.license_plate) > 1
        else None
    )
    label = (
        vehicle.vehicle.label
        if vehicle.vehicle.label and len(vehicle.vehicle.label) > 0
        else None
    )

    record = Record(
        vehicle=Vehicle(
            id=vehicle.vehicle.id,
            plate=license_plate,
            label=label,
            type=VehicleType(vehicle_type),
        ),
        trip=Trip(
            id=vehicle.trip.trip_id,
            direction=vehicle.trip.direction_id,
            route=vehicle.trip.route_id,
        ),
        agency=Agency(
            id=agency[0],
            name=agency[1],
            url=agency[2],
        ),
        timestamp=datetime.fromtimestamp(vehicle.timestamp),
    )

    logger.info("processing trip", extra={"record": record.model_dump()})

    existing_record = await Record.find_one(
        {
            "trip.id": record.trip.id,
            "agency.name": record.agency.name,
            "agency.id": record.agency.id,
            "vehicle.id": record.vehicle.id,
        }
    )
    if not existing_record:
        await record.insert()
        logger.info(
            "recorded new vehicle trip", extra={"record": record.model_dump()}
        )


async def record_all_vehicles(
    data: bytes,
    routes: list[list[str]],
    agencies: list[list[str]],
) -> None:
    """Processes all GTFS-RT vehicles concurrently."""
    gtfs = GTFSRT()
    gtfs.load(data)

    tasks = [
        asyncio.create_task(process_vehicle(vehicle, routes, agencies))
        for vehicle in gtfs.positions
    ]
    await asyncio.gather(*tasks, return_exceptions=True)

    for task in tasks:
        if isinstance(task, BaseException):
            logger.error("error processing vehicle", exc_info=task)


async def run_recorder() -> None:
    """Continuously fetches and records GTFS-RT vehicle position data every 30 seconds."""
    await transit.setup_transit_data()

    with open(
        "./data/transit/routes.txt", "r", encoding="utf-8"
    ) as routes_file, open(
        "./data/transit/agency.txt", "r", encoding="utf-8"
    ) as agencies_file:
        routes = list(csv.reader(routes_file))
        agencies = list(csv.reader(agencies_file))

    async with ClientSession() as session:
        while True:
            try:
                logger.info(
                    "fetching gtfs-rt feed data",
                    extra={"feed_url": config.FEED_URL},
                )
                _headers = config.HEADERS.copy()
                _headers["Accept"] = config.ACCEPT
                response = await session.get(
                    config.FEED_URL,
                    headers=_headers,
                )
                response.raise_for_status()
                data = await response.read()

                await record_all_vehicles(data, routes, agencies)
                await asyncio.sleep(config.FEED_UPDATE_INTERVAL)

            except asyncio.CancelledError:
                logger.info(
                    "recorder task cancelled. shutting down gracefully."
                )
                break
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.exception(
                    "unexpected error during recording", exc_info=e
                )
                await asyncio.sleep(config.FEED_UPDATE_INTERVAL)
