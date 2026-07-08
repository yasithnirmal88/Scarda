from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_reports():
    return {"status": "success", "message": "Reports endpoint ready", "data": []}


@router.post("/generate")
async def generate_report():
    return {"status": "success", "message": "Generate report endpoint ready", "data": None}
