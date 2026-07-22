from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

from app.events.events import EVENT_TYPES, Event

EventHandler = Callable[[Event], Coroutine[Any, Any, None]]

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in EVENT_TYPES:
            logger.warning("Subscribing to unknown event type: %s", event_type)
        handlers = self._subscribers[event_type]
        if handler not in handlers:
            handlers.append(handler)
            logger.debug(
                "Handler %s subscribed to %s (total: %d)",
                getattr(handler, "__name__", handler),
                event_type,
                len(handlers),
            )

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
            logger.debug(
                "Handler %s unsubscribed from %s",
                getattr(handler, "__name__", handler),
                event_type,
            )

    async def publish(self, event: Event) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        if not handlers:
            return
        logger.debug(
            "Publishing %s to %d handler(s)", event.event_type, len(handlers),
        )
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                logger.exception(
                    "Handler %s failed for event %s",
                    getattr(handler, "__name__", handler),
                    event.event_type,
                )

    def subscriber_count(self, event_type: str | None = None) -> int:
        if event_type is not None:
            return len(self._subscribers.get(event_type, []))
        return sum(len(h) for h in self._subscribers.values())
