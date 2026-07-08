from typing import Any


class WeatherService:
    async def get_current(self) -> dict[str, Any]:
        return {"status": "success", "message": "Weather service ready", "weather": None}

    async def get_history(self, start: str, end: str) -> dict[str, Any]:
        return {"status": "success", "message": "Weather history endpoint ready", "data": []}

    async def create(self, data: dict) -> dict[str, Any]:
        return {"status": "success", "message": "Create weather reading endpoint ready"}
