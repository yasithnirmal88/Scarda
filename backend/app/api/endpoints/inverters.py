from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_inverters():
    return {"status": "success", "message": "Inverters endpoint ready", "data": []}


@router.post("/")
async def create_inverter():
    return {"status": "success", "message": "Create inverter endpoint ready", "data": None}


@router.get("/{inverter_id}")
async def get_inverter(inverter_id: int):
    return {"status": "success", "message": f"Inverter {inverter_id} endpoint ready", "data": None}


@router.put("/{inverter_id}")
async def update_inverter(inverter_id: int):
    return {"status": "success", "message": f"Update inverter {inverter_id} endpoint ready", "data": None}


@router.delete("/{inverter_id}")
async def delete_inverter(inverter_id: int):
    return {"status": "success", "message": f"Delete inverter {inverter_id} endpoint ready"}
