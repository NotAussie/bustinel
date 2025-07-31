"""Module to download and extract GTFS transit data from Adelaide Metro API."""

import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from logging import getLogger

import backoff
from aiohttp import ClientSession, ClientError, ClientResponse
from utils import config

_LOGGER = getLogger(__name__)

GTFS_DIR = os.path.join(".", "data", "transit")
LOCK_FILE = os.path.join(".", "data", "transit-lock")
LOCK_TTL_DAYS = 1


@backoff.on_exception(
    backoff.expo,
    ClientError,
    max_tries=3,
    max_time=30,
    jitter=None,
)
async def fetch_gtfs_feed(
    session: ClientSession, url: str, headers: dict[str, str]
) -> ClientResponse:
    """Fetch GTFS feed and raise on non-2xx response."""
    response = await session.get(url, headers=headers)
    response.raise_for_status()
    return response


async def _write_lock_file(ttl: datetime) -> None:
    """Write lock file recording TTL timestamp."""
    timestamp = ttl.timestamp()
    with open(LOCK_FILE, "w", encoding="utf-8") as lock:
        lock.write(f"ttl={timestamp}")


async def generate_gtfs_data() -> None:
    """Download and extract GTFS zip, then update lock file.

    Raises:
        aiohttp.ClientError: When HTTP GET fails.
        zipfile.BadZipFile: When ZIP archive is invalid.
        OSError: When writing to disk fails.
    """
    _LOGGER.info("Downloading latest transit data")

    async with ClientSession() as session:
        resp = await fetch_gtfs_feed(
            session,
            config.GOOGLE_TRANSIT_FILE_URL,
            config.HEADERS,
        )
        raw_data = await resp.read()

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as tmp:
        tmp.write(raw_data)
        tmp.flush()
        with zipfile.ZipFile(tmp, "r") as archive:
            archive.extractall(GTFS_DIR)
    _LOGGER.info("Extracted new transit folder")

    lock_ttl = datetime.now() + timedelta(days=LOCK_TTL_DAYS)
    await _write_lock_file(lock_ttl)
    _LOGGER.info("Updated transit lock file")


async def setup_transit_data() -> bool:
    """Ensure GTFS data exists and is not expired. Regenerate if needed.

    Returns:
        bool: True when setup completes (regardless of regeneration).
    """
    _LOGGER.info("Setting up transit data folder")

    if not os.path.isdir(GTFS_DIR):
        await generate_gtfs_data()
        return True

    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as lock:
            content = lock.read().splitlines()
            ttl_line = content[0]
    except (OSError, IndexError):
        _LOGGER.exception("Lock file missing or malformed; regenerating")
        await generate_gtfs_data()
        return True

    if not ttl_line.startswith("ttl="):
        _LOGGER.error("Lock file invalid; regenerating")
        await generate_gtfs_data()
        return True

    try:
        expiry_ts = float(ttl_line.removeprefix("ttl="))
        if datetime.now() > datetime.fromtimestamp(expiry_ts):
            _LOGGER.warning("Transit data expired; rebuilding")
            await generate_gtfs_data()
            return True
    except ValueError:
        _LOGGER.exception("Could not parse TTL; regenerating")
        await generate_gtfs_data()
        return True

    _LOGGER.info("Transit data up-to-date")
    return True
