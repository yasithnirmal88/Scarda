from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import ClientManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    client_id = str(uuid.uuid4())[:8]

    manager: ClientManager = ws.app.state.websocket_manager

    await manager.connect(client_id, ws)
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await manager.send_to(client_id, {"type": "error", "message": "invalid JSON"})
                continue

            msg_type = msg.get("type", "")

            if msg_type == "ping":
                pong = await manager.heartbeat(client_id)
                await manager.send_to(client_id, pong)

            elif msg_type == "subscribe":
                logger.info("Client %s subscribed to events", client_id)
                await manager.send_to(client_id, {
                    "type": "subscribed",
                    "client_id": client_id,
                })

            elif msg_type == "unsubscribe":
                logger.info("Client %s unsubscribed", client_id)

            else:
                await manager.send_to(client_id, {
                    "type": "error",
                    "message": f"unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception:
        logger.exception("WebSocket error for client %s", client_id)
        await manager.disconnect(client_id)