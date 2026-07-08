from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_readings():
    return {"status": "success", "message": "Readings endpoint ready", "data": []}


@router.post("/")
async def create_reading():
    return {"status": "success", "message": "Create reading endpoint ready", "data": None}


@router.get("/live")
async def get_live_readings():
    return {"status": "success", "message": "Live readings endpoint ready", "data": []}
