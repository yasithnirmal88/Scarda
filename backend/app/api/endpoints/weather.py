from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_weather():
    return {"status": "success", "message": "Weather endpoint ready", "data": None}


@router.post("/")
async def create_weather():
    return {"status": "success", "message": "Create weather reading endpoint ready", "data": None}


@router.get("/history")
async def get_weather_history():
    return {"status": "success", "message": "Weather history endpoint ready", "data": []}
