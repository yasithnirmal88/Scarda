from __future__ import annotations

import logging
from typing import Any

from app.websocket.manager import ClientManager

logger = logging.getLogger(__name__)


class Broadcaster:
    """Publishes events to all connected WebSocket clients.

    Event types:
    - ``new_reading``     — live string reading data
    - ``alert_created``   — new alert triggered
    - ``alert_resolved``  — alert cleared
    - ``weather_update``  — latest weather conditions
    """

    def __init__(self, manager: ClientManager) -> None:
        self._manager = manager

    async def broadcast_new_reading(self, data: dict[str, Any]) -> None:
        sent = await self._manager.broadcast({
            "type": "new_reading",
            "payload": data,
        })
        logger.debug("Broadcasted new_reading to %d clients", sent)

    async def broadcast_alert_created(self, alert: dict[str, Any]) -> None:
        sent = await self._manager.broadcast({
            "type": "alert_created",
            "payload": alert,
        })
        logger.info("Broadcasted alert_created (%s) to %d clients", alert.get("alert_type"), sent)

    async def broadcast_alert_resolved(self, alert: dict[str, Any]) -> None:
        sent = await self._manager.broadcast({
            "type": "alert_resolved",
            "payload": alert,
        })
        logger.info("Broadcasted alert_resolved (%s) to %d clients", alert.get("alert_id"), sent)

    async def broadcast_weather_update(self, data: dict[str, Any]) -> None:
        sent = await self._manager.broadcast({
            "type": "weather_update",
            "payload": data,
        })
        logger.debug("Broadcasted weather_update to %d clients", sent)

    async def broadcast_heartbeat_check(self) -> None:
        cleaned = await self._manager.cleanup_stale(timeout=60.0)
        if cleaned:
            logger.info("Cleaned up %d stale WebSocket connections", cleaned)