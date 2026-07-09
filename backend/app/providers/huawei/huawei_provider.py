from datetime import datetime
from typing import Any

from app.providers.interfaces import IDataProvider


class HuaweiProvider(IDataProvider):
    """Data provider for Huawei Smart Logger API.

    Not yet implemented. All methods raise NotImplementedError
    until the API integration is complete.
    """

    async def get_current_readings(self) -> dict[str, Any]:
        raise NotImplementedError("HuaweiProvider is not implemented yet")

    async def get_weather(self) -> dict[str, Any]:
        raise NotImplementedError("HuaweiProvider is not implemented yet")

    async def get_historical_readings(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("HuaweiProvider is not implemented yet")

    async def get_historical_weather(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("HuaweiProvider is not implemented yet")

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "unavailable",
            "provider": "huawei",
            "connected": False,
            "message": "Huawei Smart Logger API integration not yet implemented",
        }
