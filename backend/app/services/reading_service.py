from typing import Any


class ReadingService:
    async def get_all(self) -> dict[str, Any]:
        return {"status": "success", "message": "Reading service ready", "readings": []}

    async def get_by_string(self, string_id: int) -> dict[str, Any]:
        return {"status": "success", "message": f"Readings for string {string_id} endpoint ready"}

    async def create(self, data: dict) -> dict[str, Any]:
        return {"status": "success", "message": "Create reading endpoint ready"}
