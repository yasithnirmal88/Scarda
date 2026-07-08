from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_inverters():
    return {"message": "Inverters list - placeholder", "inverters": [], "total": 0}


@router.post("/")
def create_inverter():
    return {"message": "Create inverter - placeholder", "inverter": None}


@router.put("/{inverter_id}")
def update_inverter(inverter_id: int):
    return {"message": f"Update inverter {inverter_id} - placeholder", "inverter": None}


@router.delete("/{inverter_id}")
def delete_inverter(inverter_id: int):
    return {"message": f"Delete inverter {inverter_id} - placeholder"}
