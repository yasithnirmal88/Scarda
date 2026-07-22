from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.reading_repository import ReadingRepository
from app.repositories.weather_repository import WeatherRepository


class AggregationService:
    """Computes aggregated telemetry over hourly, daily, weekly, and monthly windows.

    Each method returns structured data suitable for charting or export.
    """

    def __init__(self, db: Session) -> None:
        self._reading_repo = ReadingRepository(db)
        self._weather_repo = WeatherRepository(db)

    async def hourly(self, target_date: date | None = None) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        day = target_date or now.date()
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        buckets: list[dict[str, Any]] = []
        for hour in range(24):
            h_start = day_start + timedelta(hours=hour)
            h_end = h_start + timedelta(hours=1)
            buckets.append({
                "hour": hour,
                "period": h_start.isoformat(),
                "avg_power_w": self._reading_repo.average_power_between(h_start, h_end),
                "avg_voltage_v": self._reading_repo.average_voltage_between(h_start, h_end),
                "avg_current_a": self._reading_repo.average_current_between(h_start, h_end),
                "peak_power_w": self._reading_repo.peak_power_between(h_start, h_end),
                "total_energy_kwh": round(self._reading_repo.total_energy_between(h_start, h_end), 4),
                "reading_count": self._reading_repo.reading_count_between(h_start, h_end),
            })
        return buckets

    async def daily(
        self, start_date: date | None = None, days: int = 30,
    ) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        end = start_date and datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc) + timedelta(days=1) or now
        end = end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        start = end - timedelta(days=days)

        buckets: list[dict[str, Any]] = []
        cursor = start
        while cursor < end:
            d_end = cursor + timedelta(days=1)
            buckets.append({
                "date": cursor.date().isoformat(),
                "period": cursor.isoformat(),
                "avg_power_w": self._reading_repo.average_power_between(cursor, d_end),
                "avg_voltage_v": self._reading_repo.average_voltage_between(cursor, d_end),
                "avg_current_a": self._reading_repo.average_current_between(cursor, d_end),
                "peak_power_w": self._reading_repo.peak_power_between(cursor, d_end),
                "total_energy_kwh": round(self._reading_repo.total_energy_between(cursor, d_end), 2),
                "reading_count": self._reading_repo.reading_count_between(cursor, d_end),
            })
            cursor = d_end
        return buckets

    async def weekly(
        self, weeks: int = 4, end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        end = end_date and datetime(end_date.year, end_date.month, end_date.day, tzinfo=timezone.utc) or now
        end = end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        start = end - timedelta(weeks=weeks)

        buckets: list[dict[str, Any]] = []
        cursor = start
        while cursor < end:
            w_end = cursor + timedelta(weeks=1)
            buckets.append({
                "week_start": cursor.date().isoformat(),
                "week_end": (w_end - timedelta(days=1)).date().isoformat(),
                "avg_power_w": self._reading_repo.average_power_between(cursor, w_end),
                "avg_voltage_v": self._reading_repo.average_voltage_between(cursor, w_end),
                "avg_current_a": self._reading_repo.average_current_between(cursor, w_end),
                "peak_power_w": self._reading_repo.peak_power_between(cursor, w_end),
                "total_energy_kwh": round(self._reading_repo.total_energy_between(cursor, w_end), 2),
                "reading_count": self._reading_repo.reading_count_between(cursor, w_end),
            })
            cursor = w_end
        return buckets

    async def monthly(
        self, months: int = 12, end_year: int | None = None, end_month: int | None = None,
    ) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        y = end_year or now.year
        m = end_month or now.month
        _, last_day = calendar.monthrange(y, m)
        end = datetime(y, m, last_day, 23, 59, 59, tzinfo=timezone.utc) + timedelta(seconds=1)

        start_y = y - (months // 12) if months >= 12 else y
        start_m = max(1, m - (months % 12)) if months < 12 else 1
        start = datetime(start_y, start_m, 1, tzinfo=timezone.utc)

        buckets: list[dict[str, Any]] = []
        cursor = start
        while cursor < end:
            _, ld = calendar.monthrange(cursor.year, cursor.month)
            m_end = datetime(cursor.year, cursor.month, ld, 23, 59, 59, tzinfo=timezone.utc) + timedelta(seconds=1)
            buckets.append({
                "year": cursor.year,
                "month": cursor.month,
                "period": f"{cursor.year}-{cursor.month:02d}",
                "avg_power_w": self._reading_repo.average_power_between(cursor, m_end),
                "avg_voltage_v": self._reading_repo.average_voltage_between(cursor, m_end),
                "avg_current_a": self._reading_repo.average_current_between(cursor, m_end),
                "peak_power_w": self._reading_repo.peak_power_between(cursor, m_end),
                "total_energy_kwh": round(self._reading_repo.total_energy_between(cursor, m_end), 2),
                "reading_count": self._reading_repo.reading_count_between(cursor, m_end),
            })
            cursor = m_end
        return buckets