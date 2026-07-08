from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_sections():
    return {"message": "Sections list - placeholder", "sections": [], "total": 0}


@router.post("/")
def create_section():
    return {"message": "Create section - placeholder", "section": None}


@router.put("/{section_id}")
def update_section(section_id: int):
    return {"message": f"Update section {section_id} - placeholder", "section": None}


@router.delete("/{section_id}")
def delete_section(section_id: int):
    return {"message": f"Delete section {section_id} - placeholder"}
