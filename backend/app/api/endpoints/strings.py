from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_strings():
    return {"status": "success", "message": "Strings endpoint ready", "data": []}


@router.post("/")
async def create_string():
    return {"status": "success", "message": "Create string endpoint ready", "data": None}


@router.get("/{string_id}")
async def get_string(string_id: int):
    return {"status": "success", "message": f"String {string_id} endpoint ready", "data": None}


@router.put("/{string_id}")
async def update_string(string_id: int):
    return {"status": "success", "message": f"Update string {string_id} endpoint ready", "data": None}


@router.delete("/{string_id}")
async def delete_string(string_id: int):
    return {"status": "success", "message": f"Delete string {string_id} endpoint ready"}
