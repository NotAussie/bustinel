"""This utility provides a base class for background services."""

import asyncio
import logging
from abc import ABC, abstractmethod

from bubus import EventBus
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class ServiceBase(ABC):
    """
    ServiceBase is an abstract base class designed to provide a framework for creating
    services that run asynchronous tasks in the background. It manages the lifecycle
    of the task, including starting, stopping, and handling exceptions.

    Attributes:
        bus (EventBus): An instance of the EventBus used for communication or event handling.
        _task (asyncio.Task | None): The asyncio task running the service's main logic.
        _stop (asyncio.Event): An event used to signal the service to stop.
    """

    def __init__(self, bus: EventBus, redis: Redis):
        self.bus = bus
        self.redis = redis
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def start(self):
        """
        Asynchronously starts the service by creating and scheduling a task to run
        the `_run_wrapper` coroutine.
        Returns:
            asyncio.Task: The task object representing the scheduled `_run_wrapper` coroutine.
        """

        self._task = asyncio.create_task(self._run_wrapper())
        return self._task

    async def stop(self):
        """
        Stops the service by setting the internal stop event and awaiting the associated task.
        This method signals the service to stop by setting the `_stop` event. If there is an
        ongoing task associated with the service (`_task`), it waits for the task to complete
        before returning.

        Raises:
            Any exception raised by the awaited task, if `_task` is not None.
        """

        self._stop.set()
        if self._task:
            await self._task

    async def _run_wrapper(self):
        try:
            await self.runner()
        except asyncio.CancelledError:
            logger.info("%s runner cancelled cleanly", self.__class__.__name__)
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            logger.exception(
                "%s runner encountered exception: %s",
                self.__class__.__name__,
                exc,
            )
        finally:
            self._stop.set()

    @abstractmethod
    async def runner(self):
        """Override to implement your producer or background loop."""
