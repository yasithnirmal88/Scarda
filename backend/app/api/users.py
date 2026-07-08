from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_users():
    return {"message": "Users list - placeholder", "users": [], "total": 0}


@router.post("/")
def create_user():
    return {"message": "Create user - placeholder", "user": None}


@router.put("/{user_id}")
def update_user(user_id: int):
    return {"message": f"Update user {user_id} - placeholder", "user": None}


@router.delete("/{user_id}")
def delete_user(user_id: int):
    return {"message": f"Delete user {user_id} - placeholder"}
