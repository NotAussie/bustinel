"""Main application entrypoint for the Bustinel project.

This module initializes logging, sets up the MongoDB connection,
and starts the recorder task.
"""

import os
import asyncio
import logging

from pythonjsonlogger.json import JsonFormatter

from pymongo import AsyncMongoClient
from beanie import init_beanie

from recorder import run_recorder
from models import __models
from utils import config

# Logging
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)
logger = logging.getLogger(__name__)

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
