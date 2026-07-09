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

    def __init__(self, heartbeat_interval: int = 30) -> None:
        self._clients: dict[str, WebSocket] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._heartbeat_interval = heartbeat_interval

    @property
    def connected_count(self) -> int:
        return len(self._clients)

    @property
    def client_ids(self) -> list[str]:
        return list(self._clients.keys())

    async def connect(self, client_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._clients[client_id] = ws
        self._metadata[client_id] = {
            "connected_at": time.time(),
            "last_heartbeat": time.time(),
            "user_agent": ws.headers.get("user-agent", ""),
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

    def check_stale(self, timeout: float = 60.0) -> list[str]:
        now = time.time()
        stale: list[str] = []
        for client_id, meta in self._metadata.items():
            if now - meta.get("last_heartbeat", 0) > timeout:
                stale.append(client_id)
        return stale

    async def cleanup_stale(self, timeout: float = 60.0) -> int:
        stale = self.check_stale(timeout)
        for client_id in stale:
            await self.disconnect(client_id)
        return len(stale)

    @staticmethod
    async def _send(ws: WebSocket, message: dict[str, Any]) -> None:
        import json
        await ws.send_text(json.dumps(message, default=str))