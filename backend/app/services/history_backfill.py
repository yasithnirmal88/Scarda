"""Historical backfill service.

On startup, Scarda pulls historical readings (with their *original measurement
timestamps*) from the configured provider and stores them in the existing
``string_readings`` hypertable so the Tier-2 ``HistoricalBaselineProvider``
has data to compare against. This is NOT fake-data generation — every value
originates from the data provider (mock-fusionsolar in dev, real Huawei in
prod). Scarda never fabricates readings itself.

The backfill is idempotent-ish: it is skipped entirely when the database is
unavailable, and individual row insertions that fail are logged and skipped
rather than aborting startup.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import settings
from app.providers.interfaces import IDataProvider

logger = logging.getLogger(__name__)


def _parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        ts = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except (TypeError, ValueError):
        return None


async def backfill_history(
    provider: IDataProvider,
    event_bus: Any | None = None,
    *,
    days: int | None = None,
    db_session: Any | None = None,
) -> int:
    """Pull ``days`` of historical readings from the provider into TimescaleDB.

    Preserves each reading's original measurement timestamp. Returns the number
    of readings stored. When no database session is supplied, readings are
    still published on the event bus (``reading.generated``) so the existing
    ``ReadingStorageHandler`` persists them with source timestamps — this is
    the path used at startup.

    ``days`` defaults to the historical lookback window used by the baseline
    (``HISTORICAL_LOOKBACK_DAYS``), so the baseline always has at least as much
    history as it queries.
    """
    if days is None:
        days = settings.thresholds.HISTORICAL_LOOKBACK_DAYS
    days = max(1, int(days))

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    try:
        readings = await provider.get_historical_readings(start, end)
    except Exception:
        logger.warning(
            "Historical backfill: provider.get_historical_readings failed; "
            "skipping backfill",
            exc_info=True,
        )
        readings = []

    if db_session is not None:
        stored = _bulk_store(db_session, readings)
    elif event_bus is not None:
        # Publish through the event bus so ReadingStorageHandler persists each
        # reading with its original timestamp and the alert pipeline sees it.
        await event_bus.publish("reading.generated", {"readings": readings})
        stored = len(readings)
    else:
        stored = 0

    logger.info("Historical backfill: stored %d readings (%s days)", stored, days)

    # Backfill plant-level weather so the weather_readings hypertable holds the
    # full 90-day, 10-min history (used for trend/weather analysis). Each sample
    # keeps its original measurement timestamp.
    try:
        weather_points = await provider.get_historical_weather(start, end)
    except Exception:
        logger.warning(
            "Historical backfill: provider.get_historical_weather failed; "
            "skipping weather backfill",
            exc_info=True,
        )
        weather_points = []

    if weather_points and db_session is not None:
        w_stored = _bulk_store_weather(db_session, weather_points)
        logger.info(
            "Historical backfill: stored %d weather samples (%s days)", w_stored, days
        )
    elif weather_points and event_bus is not None:
        for wp in weather_points:
            await event_bus.publish("weather.updated", {"weather_data": wp})

    return stored


def _bulk_store(session: Any, readings: list[dict[str, Any]]) -> int:
    """Persist a batch of provider readings directly into ``string_readings``.

    Preserves original measurement timestamps. Resolves composite Scarda string
    ids to integer FKs (creating the section/inverter/string hierarchy by code
    as needed). Skips rows that fail to resolve rather than aborting the batch.
    """
    try:
        from app.models.telemetry.string_reading import StringReading
        from app.providers.huawei.string_identity import coerce_string_id
        from app.repositories.reading_repository import ReadingRepository
    except Exception:
        logger.warning("Historical backfill: storage models unavailable", exc_info=True)
        return 0

    repo = ReadingRepository(session)

    # Resolve each *unique* composite string id once (creating the plant
    # hierarchy by code as needed), then reuse the integer FK for every
    # reading. Without this cache, a 90-day × 40-string backfill would issue
    # one section/inverter/string lookup per reading (~500k queries).
    raw_ids = {rd.get("string_id", "0") for rd in readings}
    id_cache: dict[str, int] = {}
    for raw in raw_ids:
        sid = coerce_string_id(session, raw)
        if sid != 0:
            id_cache[str(raw)] = sid

    rows: list[StringReading] = []
    for rd in readings:
        measured_at = _parse_ts(rd.get("timestamp")) or datetime.now(timezone.utc)
        string_id = id_cache.get(str(rd.get("string_id", "0")), 0)
        if string_id == 0:
            # Couldn't resolve to a real string FK — skip rather than store
            # against the unknown-string sentinel, which would pollute history.
            continue
        rows.append(
            StringReading(
                string_id=string_id,
                recorded_at=measured_at,
                voltage=rd.get("voltage_v") or rd.get("voltage"),
                current=rd.get("current_a") or rd.get("current"),
                power=rd.get("power_w") or rd.get("power"),
                irradiance=rd.get("irradiance_wpm2") or rd.get("irradiance"),
                temperature=rd.get("temperature_c") or rd.get("temperature"),
            )
        )
    if not rows:
        return 0
    try:
        repo.bulk_create(rows)
        return len(rows)
    except Exception:
        logger.warning("Historical backfill: bulk store failed", exc_info=True)
        return 0


def _bulk_store_weather(session: Any, weather_points: list[dict[str, Any]]) -> int:
    """Persist a batch of provider weather samples into ``weather_readings``.

    Each sample keeps its original measurement timestamp so the weather
    hypertable holds a true 10-min time series aligned with ``string_readings``.
    """
    try:
        from app.models.telemetry.weather_reading import WeatherReading
        from app.repositories.weather_repository import WeatherRepository
    except Exception:
        logger.warning("Historical backfill: weather models unavailable", exc_info=True)
        return 0

    repo = WeatherRepository(session)
    rows: list[WeatherReading] = []
    for wp in weather_points:
        measured_at = _parse_ts(wp.get("timestamp")) or datetime.now(timezone.utc)
        rows.append(
            WeatherReading(
                recorded_at=measured_at,
                temperature=wp.get("temperature_c"),
                humidity=wp.get("humidity_pct"),
                irradiance=wp.get("irradiance_wpm2"),
                wind_speed=wp.get("wind_speed_mps"),
                wind_direction=wp.get("wind_direction"),
                precipitation=wp.get("precipitation_mm"),
            )
        )
    if not rows:
        return 0
    try:
        repo.bulk_create(rows)
        return len(rows)
    except Exception:
        session.rollback()
        logger.warning("Historical backfill: weather bulk store failed", exc_info=True)
        return 0
