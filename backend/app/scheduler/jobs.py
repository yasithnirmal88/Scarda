from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.events.event_bus import EventBus
from app.events.events import ReadingGenerated, SchedulerTick, WeatherUpdated

logger = logging.getLogger(__name__)


async def simulator_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[simulator_job] Simulator tick at %s", datetime.now().isoformat())

    event_bus: EventBus | None = (context or {}).get("event_bus")
    provider = (context or {}).get("provider")

    if provider is not None and event_bus is not None:
        try:
            readings = await provider.get_current_readings()
            weather = await provider.get_weather()

            reading_list: list[dict[str, Any]] = (
                readings if isinstance(readings, list) else readings.get("readings", [])
            )

            await event_bus.publish(
                ReadingGenerated(readings=reading_list, weather=weather),
            )
        except Exception:
            logger.exception("[simulator_job] Failed to publish readings/weather")


async def alert_processing_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[alert_processing_job] Alert processing cycle at %s", datetime.now().isoformat())

    event_bus: EventBus | None = (context or {}).get("event_bus")

    if event_bus is not None:
        try:
            await event_bus.publish(SchedulerTick(tick_type="alert_processing"))
        except Exception:
            logger.exception("[alert_processing_job] Failed to publish tick")


async def cleanup_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[cleanup_job] Cleanup cycle at %s", datetime.now().isoformat())

    event_bus: EventBus | None = (context or {}).get("event_bus")

    if event_bus is not None:
        try:
            await event_bus.publish(SchedulerTick(tick_type="cleanup"))
        except Exception:
            logger.exception("[cleanup_job] Failed to publish cleanup tick")


async def statistics_update_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[statistics_update_job] Statistics update at %s", datetime.now().isoformat())

    event_bus: EventBus | None = (context or {}).get("event_bus")

    if event_bus is not None:
        try:
            await event_bus.publish(SchedulerTick(tick_type="statistics_update"))
        except Exception:
            logger.exception("[statistics_update_job] Failed to publish stats tick")
