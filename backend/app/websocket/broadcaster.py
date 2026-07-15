"""Event broadcaster for WebSocket clients.

Publishes typed events (readings, alerts, weather) to connected clients.
Supports both broadcast-to-all and topic-filtered broadcasting.
"""

from __future__ import annotations

import logging

from app.websocket.manager import ClientManager

logger = logging.getLogger(__name__)

# Topic constants for subscription-based broadcasting
TOPIC_READINGS = "readings"
TOPIC_ALERTS = "alerts"
TOPIC_WEATHER = "weather"


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

    async def broadcast_new_reading(self, data: dict) -> None:
        message = {
            "type": "new_reading",
            "payload": data,
        }
        sent = await self._manager.broadcast_to_topic(TOPIC_READINGS, message)
        if sent == 0:
            sent = await self._manager.broadcast(message)
        logger.debug("Broadcasted new_reading to %d clients", sent)

    async def broadcast_alert_created(self, alert: dict) -> None:
        message = {
            "type": "alert_created",
            "payload": alert,
        }
        sent = await self._manager.broadcast_to_topic(TOPIC_ALERTS, message)
        if sent == 0:
            sent = await self._manager.broadcast(message)
        logger.info("Broadcasted alert_created (%s) to %d clients", alert.get("alert_type"), sent)

    async def broadcast_alert_resolved(self, alert: dict) -> None:
        message = {
            "type": "alert_resolved",
            "payload": alert,
        }
        sent = await self._manager.broadcast_to_topic(TOPIC_ALERTS, message)
        if sent == 0:
            sent = await self._manager.broadcast(message)
        logger.info("Broadcasted alert_resolved (%s) to %d clients", alert.get("alert_id"), sent)

    async def broadcast_weather_update(self, data: dict) -> None:
        message = {
            "type": "weather_update",
            "payload": data,
        }
        sent = await self._manager.broadcast_to_topic(TOPIC_WEATHER, message)
        if sent == 0:
            sent = await self._manager.broadcast(message)
        logger.debug("Broadcasted weather_update to %d clients", sent)

    async def broadcast_heartbeat_check(self) -> None:
        cleaned = await self._manager.cleanup_stale()
        if cleaned:
            logger.info("Cleaned up %d stale WebSocket connections", cleaned)
