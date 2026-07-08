from typing import Any


class UserService:
    async def get_all(self) -> dict[str, Any]:
        return {"status": "success", "message": "User service ready", "users": []}

    async def get_by_id(self, user_id: int) -> dict[str, Any]:
        return {"status": "success", "message": f"User {user_id} endpoint ready"}

    async def create(self, data: dict) -> dict[str, Any]:
        return {"status": "success", "message": "Create user endpoint ready"}

    async def update(self, user_id: int, data: dict) -> dict[str, Any]:
        return {"status": "success", "message": f"Update user {user_id} endpoint ready"}

    async def delete(self, user_id: int) -> dict[str, Any]:
        return {"status": "success", "message": f"Delete user {user_id} endpoint ready"}
