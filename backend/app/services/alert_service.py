from typing import Any


class AlertService:
    async def get_all(self) -> dict[str, Any]:
        return {"status": "success", "message": "Alert service ready", "alerts": []}

    async def get_by_id(self, alert_id: int) -> dict[str, Any]:
        return {"status": "success", "message": f"Alert {alert_id} endpoint ready"}

    async def create(self, data: dict) -> dict[str, Any]:
        return {"status": "success", "message": "Create alert endpoint ready"}

    async def update(self, alert_id: int, data: dict) -> dict[str, Any]:
        return {"status": "success", "message": f"Update alert {alert_id} endpoint ready"}

    async def delete(self, alert_id: int) -> dict[str, Any]:
        return {"status": "success", "message": f"Delete alert {alert_id} endpoint ready"}
