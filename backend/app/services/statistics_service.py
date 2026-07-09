from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.reading_repository import ReadingRepository
from app.repositories.inverter_repository import InverterRepository
from app.repositories.section_repository import SectionRepository
from app.repositories.string_repository import StringRepository
from app.repositories.weather_repository import WeatherRepository


class StatisticsService:
    """Computes historical statistics across daily, weekly, and monthly periods.

    All queries go through repositories — no direct SQL or model access.
    Periods use UTC boundaries and the repository's aggregate methods.
    """

    def __init__(self, db: Session) -> None:
        self._reading_repo = ReadingRepository(db)
        self._weather_repo = WeatherRepository(db)
        self._string_repo = StringRepository(db)
        self._inverter_repo = InverterRepository(db)
        self._section_repo = SectionRepository(db)

    async def get_daily_averages(
        self, target_date: date | None = None
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        day = target_date or now.date()
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        return {
            "date": day.isoformat(),
            "power": {
                "average_kw": self._reading_repo.average_power_between(start, end),
                "peak_kw": self._reading_repo.peak_power_between(start, end),
                "total_energy_kwh": round(
                    self._reading_repo.total_energy_between(start, end), 2
                ),
            },
            "voltage": {
                "average_v": self._reading_repo.average_voltage_between(start, end),
            },
            "current": {
                "average_a": self._reading_repo.average_current_between(start, end),
            },
            "temperature": {
                "average_c": self._weather_repo.average_temperature_between(start, end),
            },
            "reading_count": self._reading_repo.reading_count_between(start, end),
        }

    async def get_weekly_averages(
        self, week_end: date | None = None
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        end_date = week_end or now.date()
        end = datetime(end_date.year, end_date.month, end_date.day, tzinfo=timezone.utc) + timedelta(days=1)
        start = end - timedelta(days=7)

        return {
            "start_date": start.date().isoformat(),
            "end_date": end_date.isoformat(),
            "power": {
                "average_kw": self._reading_repo.average_power_between(start, end),
                "peak_kw": self._reading_repo.peak_power_between(start, end),
                "total_energy_kwh": round(
                    self._reading_repo.total_energy_between(start, end), 2
                ),
            },
            "voltage": {
                "average_v": self._reading_repo.average_voltage_between(start, end),
            },
            "current": {
                "average_a": self._reading_repo.average_current_between(start, end),
            },
            "temperature": {
                "average_c": self._weather_repo.average_temperature_between(start, end),
            },
            "reading_count": self._reading_repo.reading_count_between(start, end),
        }

    async def get_monthly_averages(
        self, year: int | None = None, month: int | None = None
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        y = year or now.year
        m = month or now.month

        import calendar

        start = datetime(y, m, 1, tzinfo=timezone.utc)
        last_day = calendar.monthrange(y, m)[1]
        end = datetime(y, m, last_day, 23, 59, 59, tzinfo=timezone.utc) + timedelta(seconds=1)

        return {
            "year": y,
            "month": m,
            "period": f"{y}-{m:02d}",
            "power": {
                "average_kw": self._reading_repo.average_power_between(start, end),
                "peak_kw": self._reading_repo.peak_power_between(start, end),
                "total_energy_kwh": round(
                    self._reading_repo.total_energy_between(start, end), 2
                ),
            },
            "voltage": {
                "average_v": self._reading_repo.average_voltage_between(start, end),
            },
            "current": {
                "average_a": self._reading_repo.average_current_between(start, end),
            },
            "temperature": {
                "average_c": self._weather_repo.average_temperature_between(start, end),
            },
            "reading_count": self._reading_repo.reading_count_between(start, end),
        }