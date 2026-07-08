from __future__ import annotations

from datetime import datetime, timedelta
from typing import Generator


class TimeEngine:
    """Generates timestamps for simulation cycles.

    Provides methods to create timestamps at fixed intervals for any
    duration, supporting both sequential and range-based generation.
    """

    def __init__(self, interval_minutes: int = 10) -> None:
        self.interval_minutes = interval_minutes
        self._interval = timedelta(minutes=interval_minutes)

    @property
    def interval(self) -> timedelta:
        return self._interval

    def generate_timestamps(
        self, start: datetime, end: datetime
    ) -> Generator[datetime, None, None]:
        """Yield timestamps from start (inclusive) to end (exclusive)."""
        current = start
        while current < end:
            yield current
            current += self._interval

    def generate_day(self, day: datetime | None = None) -> Generator[datetime, None, None]:
        """Yield timestamps for a full 24-hour period starting at midnight."""
        start = (day or datetime.now()).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=1)
        yield from self.generate_timestamps(start, end)

    def generate_week(self, week_start: datetime | None = None) -> Generator[datetime, None, None]:
        """Yield timestamps for 7 full days."""
        start = (week_start or datetime.now()).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        for day_offset in range(7):
            day_start = start + timedelta(days=day_offset)
            yield from self.generate_day(day_start)

    def generate_custom(self, hours: int) -> Generator[datetime, None, None]:
        """Yield timestamps for a custom number of hours."""
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        end = now + timedelta(hours=hours)
        yield from self.generate_timestamps(now, end)

    def count_timestamps(self, duration_hours: float) -> int:
        """Return how many timestamps fit in a given duration."""
        return int((duration_hours * 60) / self.interval_minutes)
