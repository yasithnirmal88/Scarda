from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


async def simulator_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[simulator_job] Simulator tick at %s", datetime.now().isoformat())

    broadcaster = (context or {}).get("broadcaster")
    provider = (context or {}).get("provider")

    if provider is not None and broadcaster is not None:
        try:
            readings = await provider.get_current_readings()
            await broadcaster.broadcast_new_reading(readings)

            weather = await provider.get_weather()
            await broadcaster.broadcast_weather_update(weather)
        except Exception:
            logger.exception("[simulator_job] Failed to broadcast readings/weather")


async def alert_processing_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[alert_processing_job] Alert processing cycle at %s", datetime.now().isoformat())

    broadcaster = (context or {}).get("broadcaster")

    if broadcaster is not None:
        try:
            await broadcaster.broadcast_heartbeat_check()
        except Exception:
            logger.exception("[alert_processing_job] Failed heartbeat check")


async def cleanup_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[cleanup_job] Cleanup cycle at %s", datetime.now().isoformat())

    broadcaster = (context or {}).get("broadcaster")
    if broadcaster is not None:
        try:
            await broadcaster.broadcast_heartbeat_check()
        except Exception:
            logger.exception("[cleanup_job] Failed heartbeat check")


async def statistics_update_job(context: dict[str, Any] | None = None) -> None:
    logger.info("[statistics_update_job] Statistics update at %s", datetime.now().isoformat())