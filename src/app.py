"""Bustinel application entrypoint."""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import logfire
import sentry_sdk
from beanie import init_beanie
from bubus import EventBus
from pymongo import AsyncMongoClient
from pythonjsonlogger.json import JsonFormatter
from redis.asyncio import Redis
from sentry_sdk.integrations.logging import EventHandler
from tortoise import Tortoise

from models.beanie import collections
from services.meta import MetaService
from services.realtime import RealtimeService
from utilities import Settings

bus = EventBus(parallel_handlers=True)

# Logging
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler, EventHandler(logging.WARNING)],
)

# Sentry
sentry_sdk.init(
    send_default_pii=True,
    traces_sample_rate=1.0,
    environment=Settings.ENVIRONMENT,
)

# Logfire
logfire.configure(
    environment=Settings.ENVIRONMENT,
    service_name="bustinel",
    console=False,
)
logfire.install_auto_tracing(
    ["bubus", "tortoise", "beanie", "services"],
    min_duration=100,
    check_imported_modules="ignore",
)
logfire.log_slow_async_callbacks()
logfire.instrument_pydantic()
logfire.instrument_aiohttp_client()
logfire.instrument_pymongo(True)
logfire.instrument_sqlite3()


@asynccontextmanager
async def lifespan():
    """Application lifespan context manager."""

    os.makedirs("/app/data", exist_ok=True)
    await Tortoise.init(
        db_url="sqlite://data/db.sqlite3",
        modules={"models": ["models.tortoise"]},
    )
    await Tortoise.generate_schemas()

    mongo = AsyncMongoClient(
        Settings.MONGODB_URI,
    )
    await init_beanie(
        mongo[Settings.MONGODB_DATABASE], document_models=collections
    )

    redis = Redis.from_url(Settings.REDIS_URI, decode_responses=True)

    bus._start()  # pylint: disable=protected-access

    services = [
        MetaService(bus, redis),
        RealtimeService(bus, redis),
    ]

    for service in services:
        await service.start()
    yield
    for service in services:
        await service.stop()

    await bus.stop(timeout=5, clear=True)
    await Tortoise.close_connections()


async def main():
    """Main application entrypoint."""
    async with lifespan():
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
