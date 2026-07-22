from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.reading_repository import ReadingRepository
from app.repositories.weather_repository import WeatherRepository


class TelemetryStatisticsService:
    """Computes per-signal statistics for current, voltage, power, and irradiance.

    Unlike the top-level StatisticsService, these methods accept raw
    window bounds and let the caller define the period.  Each returns
    a flat dict of descriptive statistics for a single signal.
    """

    def __init__(self, db: Session) -> None:
        self._reading_repo = ReadingRepository(db)
        self._weather_repo = WeatherRepository(db)

    async def average_current(
        self, start: datetime, end: datetime,
    ) -> dict[str, Any]:
        avg = self._reading_repo.average_current_between(start, end)
        return {
            "signal": "current_a",
            "average": avg,
            "unit": "A",
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
        }

    async def average_voltage(
        self, start: datetime, end: datetime,
    ) -> dict[str, Any]:
        avg = self._reading_repo.average_voltage_between(start, end)
        return {
            "signal": "voltage",
            "average": avg,
            "unit": "V",
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
        }

    async def average_power(
        self, start: datetime, end: datetime,
    ) -> dict[str, Any]:
        avg = self._reading_repo.average_power_between(start, end)
        peak = self._reading_repo.peak_power_between(start, end)
        energy_kwh = self._reading_repo.total_energy_between(start, end)
        return {
            "signal": "power",
            "average_w": avg,
            "peak_w": peak,
            "total_energy_kwh": round(energy_kwh, 2),
            "unit": "W",
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
        }

    async def average_irradiance(
        self, start: datetime, end: datetime,
    ) -> dict[str, Any]:
        count = self._reading_repo.reading_count_between(start, end)
        readings = self._reading_repo.find_between(start, end)
        values = [r.irradiance for r in readings if r.irradiance is not None]
        avg = sum(values) / len(values) if values else None
        peak = max(values) if values else None
        return {
            "signal": "irradiance",
            "average_wpm2": round(avg, 2) if avg is not None else None,
            "peak_wpm2": round(peak, 2) if peak is not None else None,
            "unit": "W/m²",
            "reading_count": count,
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
        }

    async def all_signals(
        self, start: datetime, end: datetime,
    ) -> dict[str, Any]:
        return {
            "current": await self.average_current(start, end),
            "voltage": await self.average_voltage(start, end),
            "power": await self.average_power(start, end),
            "irradiance": await self.average_irradiance(start, end),
        }