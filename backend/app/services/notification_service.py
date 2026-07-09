from __future__ import annotations

from typing import Any


class NotificationService:
    """Placeholder for future notification delivery.

    Will handle:
    - Email alerts for critical system events
    - Push notifications for real-time inverter/string failures
    - SMS gateway integration
    - Notification preferences per user
    - Rate-limited digest mode
    """

    async def send(self, recipient: str, subject: str, body: str) -> dict[str, Any]:
        return {
            "status": "success",
            "message": f"Notification placeholder: would send to {recipient}",
        }

    async def get_pending(self) -> dict[str, Any]:
        return {"status": "success", "message": "No pending notifications", "notifications": []}

    async def mark_sent(self, notification_id: str) -> dict[str, Any]:
        return {"status": "success", "message": f"Notification {notification_id} marked as sent"}