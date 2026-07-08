from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class IDataProvider(ABC):
    @abstractmethod
    async def get_current_readings(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_weather(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_historical_data(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        pass
