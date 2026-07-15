"""WebSocket client manager.

Handles connect/disconnect lifecycle, heartbeat monitoring,
broadcast to all or filtered subsets of clients, and stale
connection cleanup using configurable timeout values.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ClientManager:
    """Manages connected WebSocket clients.

    Provides connect/disconnect lifecycle, heartbeat monitoring,
    and broadcast to all or filtered subsets of clients.
    """

    def __init__(self, heartbeat_interval: int = 30, stale_timeout: float = 60.0) -> None:
        self._clients: dict[str, WebSocket] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._heartbeat_interval = heartbeat_interval
        self._stale_timeout = stale_timeout

    @property
    def connected_count(self) -> int:
        return len(self._clients)

    @property
    def client_ids(self) -> list[str]:
        return list(self._clients.keys())

    @property
    def stale_timeout(self) -> float:
        return self._stale_timeout

    async def connect(self, client_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._clients[client_id] = ws
        self._metadata[client_id] = {
            "connected_at": time.time(),
            "last_heartbeat": time.time(),
            "user_agent": ws.headers.get("user-agent", ""),
            "subscriptions": set(),
        }
        logger.info("WebSocket client connected: %s (total: %d)", client_id, self.connected_count)
        await self._send(ws, {"type": "connected", "client_id": client_id})

    async def disconnect(self, client_id: str) -> None:
        ws = self._clients.pop(client_id, None)
        self._metadata.pop(client_id, None)
        if ws is not None:
            try:
                await ws.close()
            except Exception:
                pass
        logger.info("WebSocket client disconnected: %s (total: %d)", client_id, self.connected_count)

    async def heartbeat(self, client_id: str) -> dict[str, Any]:
        meta = self._metadata.get(client_id)
        if meta is not None:
            meta["last_heartbeat"] = time.time()
        return {"type": "pong", "client_id": client_id}

    def is_connected(self, client_id: str) -> bool:
        return client_id in self._clients

    def get_client_info(self, client_id: str) -> dict[str, Any] | None:
        return self._metadata.get(client_id)

    # --- Subscription management -------------------------------------------

    def subscribe(self, client_id: str, topic: str) -> bool:
        """Subscribe a client to a topic. Returns True if successful."""
        meta = self._metadata.get(client_id)
        if meta is None:
            return False
        meta["subscriptions"].add(topic)
        logger.info("Client %s subscribed to topic: %s", client_id, topic)
        return True

    def unsubscribe(self, client_id: str, topic: str) -> bool:
        """Unsubscribe a client from a topic. Returns True if successful."""
        meta = self._metadata.get(client_id)
        if meta is None:
            return False
        meta["subscriptions"].discard(topic)
        logger.info("Client %s unsubscribed from topic: %s", client_id, topic)
        return True

    def get_subscriptions(self, client_id: str) -> set[str]:
        """Return the set of topics a client is subscribed to."""
        meta = self._metadata.get(client_id)
        if meta is None:
            return set()
        return meta["subscriptions"]

    def is_subscribed(self, client_id: str, topic: str) -> bool:
        """Check if a client is subscribed to a given topic."""
        return topic in self.get_subscriptions(client_id)

    # --- Broadcasting ------------------------------------------------------

    async def broadcast(self, message: dict[str, Any]) -> int:
        sent = 0
        dead: list[str] = []
        for client_id, ws in self._clients.items():
            try:
                await self._send(ws, message)
                sent += 1
            except Exception:
                dead.append(client_id)
        for client_id in dead:
            await self.disconnect(client_id)
        return sent

    async def broadcast_to_topic(self, topic: str, message: dict[str, Any]) -> int:
        """Broadcast a message only to clients subscribed to the given topic."""
        sent = 0
        dead: list[str] = []
        for client_id, ws in self._clients.items():
            if not self.is_subscribed(client_id, topic):
                continue
            try:
                await self._send(ws, message)
                sent += 1
            except Exception:
                dead.append(client_id)
        for client_id in dead:
            await self.disconnect(client_id)
        return sent

    async def broadcast_to(self, client_ids: list[str], message: dict[str, Any]) -> int:
        sent = 0
        for client_id in client_ids:
            ws = self._clients.get(client_id)
            if ws is None:
                continue
            try:
                await self._send(ws, message)
                sent += 1
            except Exception:
                await self.disconnect(client_id)
        return sent

    async def send_to(self, client_id: str, message: dict[str, Any]) -> bool:
        ws = self._clients.get(client_id)
        if ws is None:
            return False
        try:
            await self._send(ws, message)
            return True
        except Exception:
            await self.disconnect(client_id)
            return False

    # --- Stale connection management ---------------------------------------

    def check_stale(self, timeout: float | None = None) -> list[str]:
        """Return client IDs whose heartbeat has timed out."""
        effective_timeout = timeout if timeout is not None else self._stale_timeout
        now = time.time()
        stale: list[str] = []
        for client_id, meta in self._metadata.items():
            if now - meta.get("last_heartbeat", 0) > effective_timeout:
                stale.append(client_id)
        return stale

    async def cleanup_stale(self, timeout: float | None = None) -> int:
        """Disconnect and remove stale clients. Returns count removed."""
        stale = self.check_stale(timeout)
        for client_id in stale:
            await self.disconnect(client_id)
        return len(stale)

    @staticmethod
    async def _send(ws: WebSocket, message: dict[str, Any]) -> None:
        import json
        await ws.send_text(json.dumps(message, default=str))
