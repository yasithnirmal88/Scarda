from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
def login():
    return {"message": "Login endpoint - placeholder", "token": None}


@router.post("/register")
def register():
    return {"message": "Register endpoint - placeholder", "user": None}
