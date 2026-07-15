"""Background job implementations for the scheduler.

Each job is an async function that receives a shared context dictionary
containing the event bus, broadcaster, provider, and app references.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from app.events.event_bus import EventBus
from app.events.events import ReadingGenerated, SchedulerTick, WeatherUpdated

logger = logging.getLogger(__name__)


async def simulator_job(context: dict[str, Any] | None = None) -> None:
    """Fetch latest readings and weather from the provider and publish via event bus."""
    logger.info("[simulator_job] Simulator tick at %s", datetime.now(timezone.utc).isoformat())

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


async def _publish_tick_job(
    job_name: str,
    tick_type: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Shared logic for jobs that publish a SchedulerTick event via the event bus."""
    logger.info("[%s] Cycle at %s", job_name, datetime.now(timezone.utc).isoformat())

    event_bus: EventBus | None = (context or {}).get("event_bus")

    if event_bus is not None:
        try:
            await event_bus.publish(SchedulerTick(tick_type=tick_type))
        except Exception:
            logger.exception("[%s] Failed to publish tick", job_name)


async def alert_processing_job(context: dict[str, Any] | None = None) -> None:
    """Publish an alert processing tick event."""
    await _publish_tick_job("alert_processing_job", "alert_processing", context)


async def cleanup_job(context: dict[str, Any] | None = None) -> None:
    """Publish a cleanup tick event."""
    await _publish_tick_job("cleanup_job", "cleanup", context)


async def statistics_update_job(context: dict[str, Any] | None = None) -> None:
    """Publish a statistics update tick event."""
    await _publish_tick_job("statistics_update_job", "statistics_update", context)
