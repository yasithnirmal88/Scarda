from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_alerts():
    return {"status": "success", "message": "Alerts endpoint ready", "data": []}


@router.post("/")
async def create_alert():
    return {"status": "success", "message": "Create alert endpoint ready", "data": None}


@router.get("/{alert_id}")
async def get_alert(alert_id: int):
    return {"status": "success", "message": f"Alert {alert_id} endpoint ready", "data": None}


@router.put("/{alert_id}")
async def update_alert(alert_id: int):
    return {"status": "success", "message": f"Update alert {alert_id} endpoint ready", "data": None}


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    return {"status": "success", "message": f"Delete alert {alert_id} endpoint ready"}
