"""
This module provides the `GTFSRT` utility class for parsing and extracting information from GTFS-realtime (GTFS-RT) feed data.
It offers methods to load GTFS-RT data from bytes and properties to access alerts, trip updates, vehicle positions, and all entities
from the parsed feed. The module relies on protocol buffer message classes (`FeedMessage`, `Alert`, `TripUpdate`, `VehiclePosition`)
defined in the `gtfsr_proto` submodule.

Classes:
    GTFSRT: Utility class for parsing and extracting information from GTFS-realtime feed data.
"""

from typing import Tuple, Union, List
import logging

from .gtfsr_proto import (  # pylint: disable=no-name-in-module
    FeedMessage,
    Alert,
    TripUpdate,
    VehiclePosition,
)

logger = logging.getLogger(__name__)


class GTFSRT:
    """Utility class for parsing and extracting information from GTFS-realtime feed data.

    Attributes:
        feed: The parsed GTFS-realtime feed message.
    """

    def __init__(self) -> None:
        """Initializes an empty GTFS-RT object."""
        self.feed = FeedMessage()

    def load(self, data: bytes) -> bool:
        """Parses GTFS feed data from a bytes object.

        Args:
            data: Raw GTFS feed data in bytes format.

        Returns:
            True if the data was successfully parsed; False otherwise.
        """
        try:
            feed = FeedMessage()
            feed.ParseFromString(data)
            self.feed = feed
            return True
        except (
            AttributeError,
            TypeError,
            ValueError,
            IndexError,
            KeyError,
        ) as e:
            logger.error(
                "failed to parse bytes into new feed content", exc_info=e
            )
            return False

    @property
    def alerts(self) -> List[Alert]:
        """Returns the list of alerts extracted from the GTFS feed.

        Returns:
            A list of Alert messages in the GTFS feed.
        """
        return [
            entity.alert
            for entity in self.feed.entity
            if entity.HasField("alert")
        ]

    @property
    def alerts_and_ids(self) -> List[Tuple[str, Alert]]:
        """Returns a list of (entity_id, Alert) tuples from the GTFS feed.

        Returns:
            A list of tuples, each containing an entity ID and the corresponding Alert.
        """
        return [
            (entity.id, entity.alert)
            for entity in self.feed.entity
            if entity.HasField("alert")
        ]

    @property
    def updates(self) -> List[TripUpdate]:
        """Returns the list of trip updates extracted from the GTFS feed.

        Returns:
            A list of TripUpdate messages in the GTFS feed.
        """
        return [
            entity.trip_update
            for entity in self.feed.entity
            if entity.HasField("trip_update")
        ]

    @property
    def positions(self) -> List[VehiclePosition]:
        """Returns the list of vehicle positions extracted from the GTFS feed.

        Returns:
            A list of VehiclePosition messages in the GTFS feed.
        """
        return [
            entity.vehicle
            for entity in self.feed.entity
            if entity.HasField("vehicle")
        ]

    @property
    def all(self) -> List[Union[Alert, VehiclePosition, TripUpdate]]:
        """Returns all GTFS-realtime entities in the feed.

        Returns:
            A list containing all Alert, VehiclePosition, and TripUpdate entities.
        """
        entities = []
        for entity in self.feed.entity:
            if entity.HasField("alert"):
                entities.append(entity.alert)
            if entity.HasField("vehicle"):
                entities.append(entity.vehicle)
            if entity.HasField("trip_update"):
                entities.append(entity.trip_update)
        return entities
