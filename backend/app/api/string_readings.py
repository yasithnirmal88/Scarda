from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_string_readings():
    return {"message": "String readings list - placeholder", "readings": [], "total": 0}


@router.post("/")
def create_string_reading():
    return {"message": "Create string reading - placeholder", "reading": None}
