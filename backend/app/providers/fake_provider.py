from datetime import datetime
from typing import Any

from app.providers.interfaces import IDataProvider


class FakeDataProvider(IDataProvider):
    async def get_current_readings(self) -> dict[str, Any]:
        return {
            "total_power": 2450.5,
            "daily_energy": 18500.0,
            "active_inverters": 34,
            "total_inverters": 36,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_weather(self) -> dict[str, Any]:
        return {
            "temperature": 28.5,
            "humidity": 65.0,
            "irradiance": 850.0,
            "wind_speed": 12.3,
            "wind_direction": "NNE",
            "precipitation": 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_historical_data(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "power": 2350.0,
                "energy": 15000.0,
            }
        ]
