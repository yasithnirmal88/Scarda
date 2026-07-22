from __future__ import annotations

from abc import ABC, abstractmethod

from app.events.event_bus import EventBus
from app.events.events import Event, EVENT_TYPES


class EventSubscriber(ABC):
    @abstractmethod
    async def handle(self, event: Event) -> None: ...

    def subscribe(self, event_bus: EventBus, event_type: str) -> None:
        if event_type not in EVENT_TYPES:
            from logging import getLogger

            getLogger(__name__).warning(
                "Subscribing to unknown event type: %s", event_type,
            )
        event_bus.subscribe(event_type, self.handle)

    def unsubscribe(self, event_bus: EventBus, event_type: str) -> None:
        event_bus.unsubscribe(event_type, self.handle)
