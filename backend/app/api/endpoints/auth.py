from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"status": "success", "message": "Login endpoint ready", "token": None}


@router.post("/register")
async def register():
    return {"status": "success", "message": "Register endpoint ready", "user": None}


@router.post("/refresh")
async def refresh():
    return {"status": "success", "message": "Token refresh endpoint ready"}
