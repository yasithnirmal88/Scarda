from __future__ import annotations

from app.events.event_bus import EventBus
from app.events.events import Event


class EventPublisherMixin:
    _event_bus: EventBus

    async def publish_event(self, event: Event) -> None:
        await self._event_bus.publish(event)
