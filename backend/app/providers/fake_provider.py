from datetime import datetime
from typing import Any

from app.providers.base_provider import IDataProvider


class FakeDataProvider(IDataProvider):
    """Data provider that returns hardcoded placeholder data."""

    async def get_current_readings(self) -> dict[str, Any]:
        return {
            "total_power_kw": 2450.5,
            "daily_energy_kwh": 18500.0,
            "active_inverters": 34,
            "total_inverters": 36,
            "readings": [
                {"string_id": "SEC01-INV01-STR01", "current_a": 9.4, "voltage_v": 820.0, "power_w": 7708.0},
                {"string_id": "SEC01-INV01-STR02", "current_a": 8.7, "voltage_v": 815.0, "power_w": 7090.5},
                {"string_id": "SEC01-INV01-STR03", "current_a": 9.1, "voltage_v": 818.0, "power_w": 7443.8},
            ],
            "timestamp": datetime.now().isoformat(),
        }

    async def get_weather(self) -> dict[str, Any]:
        return {
            "temperature_c": 28.5,
            "humidity_pct": 65.0,
            "irradiance_wpm2": 850.0,
            "wind_speed_mps": 12.3,
            "wind_direction": "NNE",
            "precipitation_mm": 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_historical_readings(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        return [
            {
                "string_id": "SEC01-INV01-STR01",
                "timestamp": datetime.now().isoformat(),
                "current_a": 9.2,
                "voltage_v": 818.0,
                "power_w": 7525.6,
            }
        ]

    async def get_historical_weather(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "temperature_c": 27.0,
                "humidity_pct": 68.0,
                "irradiance_wpm2": 800.0,
            }
        ]

    async def health_check(self) -> dict[str, Any]:
        return {"status": "healthy", "provider": "fake", "connected": True}
