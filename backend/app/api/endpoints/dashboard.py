from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.deps import get_alert_engine, get_provider
from app.providers.interfaces import IDataProvider
from app.services.alert_engine import AlertEngine
from app.services.dashboard_service import DashboardService

router = APIRouter()


def _try_db():
    from app.database import get_db
    try:
        return next(get_db())
    except Exception:
        return None


@router.get("/")
async def get_dashboard(
    provider: IDataProvider = Depends(get_provider),
    alert_engine: AlertEngine = Depends(get_alert_engine),
):
    now = datetime.now(timezone.utc)
    db = _try_db()

    if db is not None:
        try:
            service = DashboardService(provider, db)
            return await service.get_dashboard()
        except Exception:
            pass

    readings_data = await provider.get_current_readings()
    weather_data = await provider.get_weather()
    active_alerts = alert_engine.get_active_alerts()

    total_power = readings_data.get("total_power_kw", 0.0)
    raw_readings = readings_data.get("readings", [])

    alerts_by_severity: dict[str, int] = {"critical": 0, "warning": 0, "info": 0}
    for a in active_alerts:
        sev = getattr(a, "severity", "info")
        alerts_by_severity[str(sev)] = alerts_by_severity.get(str(sev), 0) + 1

    return {
        "power": {
            "total_power_kw": total_power,
            "daily_energy_kwh": 0.0,
            "peak_power_kw": max(
                (r.get("power_w", 0) for r in raw_readings),
                default=0,
            ),
        },
        "plant": {
            "total_sections": 4,
            "total_inverters": 36,
            "total_strings": 864,
            "active_inverters": readings_data.get("active_inverters", 0),
        },
        "weather": {
            "temperature_c": weather_data.get("temperature_c"),
            "humidity_pct": weather_data.get("humidity_pct"),
            "irradiance_wpm2": weather_data.get("irradiance_wpm2"),
            "wind_speed_mps": weather_data.get("wind_speed_mps"),
            "wind_direction": weather_data.get("wind_direction"),
            "precipitation_mm": weather_data.get("precipitation_mm"),
            "description": weather_data.get("description"),
        },
        "alerts": {
            "total": len(active_alerts),
            "critical": alerts_by_severity.get("critical", 0),
            "warning": alerts_by_severity.get("warning", 0),
            "info": alerts_by_severity.get("info", 0),
        },
        "timestamp": now.isoformat(),
    }
