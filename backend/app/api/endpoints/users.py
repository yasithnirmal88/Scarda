from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users():
    return {"status": "success", "message": "Users endpoint ready", "data": []}


@router.post("/")
async def create_user():
    return {"status": "success", "message": "Create user endpoint ready", "data": None}


@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"status": "success", "message": f"User {user_id} endpoint ready", "data": None}


@router.put("/{user_id}")
async def update_user(user_id: int):
    return {"status": "success", "message": f"Update user {user_id} endpoint ready", "data": None}


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    return {"status": "success", "message": f"Delete user {user_id} endpoint ready"}
