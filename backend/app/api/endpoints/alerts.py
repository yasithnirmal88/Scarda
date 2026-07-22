from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_alert_engine
from app.services.alert_engine import AlertEngine

router = APIRouter()


@router.get("/")
async def get_alerts(
    alert_engine: AlertEngine = Depends(get_alert_engine),
):
    active = alert_engine.get_active_alerts()
    data = [
        {
            "alert_id": a.alert_id,
            "timestamp": a.timestamp.isoformat() if hasattr(a.timestamp, "isoformat") else str(a.timestamp),
            "section": a.section,
            "inverter": a.inverter,
            "string": a.string,
            "alert_type": a.alert_type,
            "expected_value": a.expected_value,
            "actual_value": a.actual_value,
            "deviation_pct": a.deviation_pct,
            "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
            "status": a.status.value if hasattr(a.status, "value") else str(a.status),
            "reason": a.reason,
            "recommendation": a.recommendation,
        }
        for a in active
    ]
    return {"status": "success", "data": data, "total": len(data)}


@router.get("/history")
async def get_alert_history(
    alert_engine: AlertEngine = Depends(get_alert_engine),
    limit: int = 100,
):
    history = alert_engine.get_alert_history(limit)
    data = [
        {
            "alert_id": a.alert_id,
            "timestamp": a.timestamp.isoformat() if hasattr(a.timestamp, "isoformat") else str(a.timestamp),
            "section": a.section,
            "inverter": a.inverter,
            "string": a.string,
            "alert_type": a.alert_type,
            "expected_value": a.expected_value,
            "actual_value": a.actual_value,
            "deviation_pct": a.deviation_pct,
            "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
            "status": a.status.value if hasattr(a.status, "value") else str(a.status),
            "reason": a.reason,
        }
        for a in history
    ]
    return {"status": "success", "data": data, "total": len(data)}


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    alert_engine: AlertEngine = Depends(get_alert_engine),
):
    result = alert_engine.acknowledge_alert(alert_id)
    if result is None:
        return {"status": "error", "message": f"Alert {alert_id} not found"}
    return {"status": "success", "message": f"Alert {alert_id} acknowledged"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    alert_engine: AlertEngine = Depends(get_alert_engine),
):
    result = alert_engine.resolve_alert(alert_id)
    if result is None:
        return {"status": "error", "message": f"Alert {alert_id} not found"}
    return {"status": "success", "message": f"Alert {alert_id} resolved"}
