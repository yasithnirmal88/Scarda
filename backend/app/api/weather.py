from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_weather():
    return {"message": "Weather data - placeholder", "weather": None}


@router.post("/")
def create_weather():
    return {"message": "Create weather reading - placeholder", "weather": None}
