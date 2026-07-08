from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_alerts():
    return {"message": "Alerts list - placeholder", "alerts": [], "total": 0}


@router.post("/")
def create_alert():
    return {"message": "Create alert - placeholder", "alert": None}


@router.put("/{alert_id}")
def update_alert(alert_id: int):
    return {"message": f"Update alert {alert_id} - placeholder", "alert": None}


@router.delete("/{alert_id}")
def delete_alert(alert_id: int):
    return {"message": f"Delete alert {alert_id} - placeholder"}
