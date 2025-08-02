"""Main application entrypoint for the Bustinel project.

This module initializes logging, sets up the MongoDB connection,
and starts the recorder task.
"""

import os
import asyncio
import logging

from pythonjsonlogger.json import JsonFormatter

from beanie import init_beanie
from pymongo import AsyncMongoClient

import sentry_sdk
from sentry_sdk.types import Event
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from recorder import run_recorder
from models import __models
from utils import config

# Logging
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(handlers=[handler], level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


# Sentry
def _sentry_before_send(event: Event, _):
    tags = event.get("tags")
    if tags is None:
        tags = {}
        event["tags"] = tags
    tags["feed"] = config.FEED_URL
    return event


if config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        integrations=[
            LoggingIntegration(
                level=config.LOG_LEVEL,
                event_level=logging.ERROR,
            ),
            AsyncioIntegration(),
            AioHttpIntegration(),
        ],
        traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
        before_send=_sentry_before_send,
    )

# Initialisation
os.makedirs("data", exist_ok=True)
mongo = AsyncMongoClient(config.MONGODB_URL)


async def main() -> None:
    await init_beanie(mongo.bustinel, document_models=__models)

    task = asyncio.create_task(run_recorder())

    try:
        await task
    except asyncio.CancelledError:
        logger.debug("recorder task was cancelled")


loop = asyncio.new_event_loop()
try:
    logger.info("starting")
    loop.run_until_complete(main())
    loop.run_forever()
except KeyboardInterrupt:
    loop.stop()
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
