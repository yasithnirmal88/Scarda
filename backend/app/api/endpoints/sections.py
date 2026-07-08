from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_sections():
    return {"status": "success", "message": "Sections endpoint ready", "data": []}


@router.post("/")
async def create_section():
    return {"status": "success", "message": "Create section endpoint ready", "data": None}


@router.get("/{section_id}")
async def get_section(section_id: int):
    return {"status": "success", "message": f"Section {section_id} endpoint ready", "data": None}


@router.put("/{section_id}")
async def update_section(section_id: int):
    return {"status": "success", "message": f"Update section {section_id} endpoint ready", "data": None}


@router.delete("/{section_id}")
async def delete_section(section_id: int):
    return {"status": "success", "message": f"Delete section {section_id} endpoint ready"}
