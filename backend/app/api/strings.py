from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_strings():
    return {"message": "Strings list - placeholder", "strings": [], "total": 0}


@router.post("/")
def create_string():
    return {"message": "Create string - placeholder", "string": None}


@router.put("/{string_id}")
def update_string(string_id: int):
    return {"message": f"Update string {string_id} - placeholder", "string": None}


@router.delete("/{string_id}")
def delete_string(string_id: int):
    return {"message": f"Delete string {string_id} - placeholder"}
