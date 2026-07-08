from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_settings():
    return {"status": "success", "message": "Settings endpoint ready", "data": []}


@router.put("/")
async def update_settings():
    return {"status": "success", "message": "Update settings endpoint ready", "data": None}
