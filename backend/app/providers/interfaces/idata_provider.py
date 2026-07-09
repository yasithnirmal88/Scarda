from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class IDataProvider(ABC):
    """Abstract interface for all data providers.

    The rest of the application must depend only on this interface.
    No service should know which concrete provider is being used.
    """

    @abstractmethod
    async def get_current_readings(self) -> dict[str, Any]:
        """Return current readings for all strings."""

    @abstractmethod
    async def get_weather(self) -> dict[str, Any]:
        """Return current weather data."""

    @abstractmethod
    async def get_historical_readings(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        """Return historical string readings within a time range."""

    @abstractmethod
    async def get_historical_weather(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        """Return historical weather data within a time range."""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Return the health status of the data source."""
