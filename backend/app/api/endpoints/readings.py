from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_provider
from app.providers.interfaces import IDataProvider

router = APIRouter()


def _try_repo(name: str):
    from app.database import get_db
    try:
        db = next(get_db())
        if name == "reading":
            from app.repositories.reading_repository import ReadingRepository
            return ReadingRepository(db)
        if name == "string":
            from app.repositories.string_repository import StringRepository
            return StringRepository(db)
    except Exception:
        return None
    return None


@router.get("/")
async def get_readings(
    provider: IDataProvider = Depends(get_provider),
    limit: int = Query(100, ge=1, le=1000),
):
    readings = await provider.get_current_readings()
    raw = readings.get("readings", [])

    repo = _try_repo("reading")
    stored = []
    if repo is not None:
        try:
            from datetime import datetime, timedelta, timezone
            from app.models.telemetry.string_reading import StringReading

            end = datetime.now(timezone.utc)
            start = end - timedelta(hours=24)
            results = repo.find_between(start, end)
            stored = [
                {
                    "id": r.id,
                    "string_id": r.string_id,
                    "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
                    "voltage": r.voltage,
                    "current": r.current,
                    "power": r.power,
                    "temperature": r.temperature,
                    "irradiance": r.irradiance,
                }
                for r in results[-limit:]
            ]
        except Exception:
            pass

    return {
        "status": "success",
        "current": raw,
        "history": stored,
        "total_power_kw": readings.get("total_power_kw"),
        "active_inverters": readings.get("active_inverters"),
        "timestamp": readings.get("timestamp"),
    }


@router.get("/current")
async def get_current_readings(
    provider: IDataProvider = Depends(get_provider),
):
    readings = await provider.get_current_readings()
    return {
        "status": "success",
        "data": readings.get("readings", []),
        "total_power_kw": readings.get("total_power_kw"),
        "active_inverters": readings.get("active_inverters"),
        "timestamp": readings.get("timestamp"),
    }


@router.get("/history")
async def get_reading_history(
    limit: int = Query(100, ge=1, le=1000),
):
    repo = _try_repo("reading")
    if repo is None:
        return {"status": "success", "data": [], "message": "Database not available"}

    try:
        from datetime import datetime, timedelta, timezone

        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=24)
        results = repo.find_between(start, end)
        data = [
            {
                "id": r.id,
                "string_id": r.string_id,
                "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
                "voltage": r.voltage,
                "current": r.current,
                "power": r.power,
                "temperature": r.temperature,
                "irradiance": r.irradiance,
            }
            for r in results[-limit:]
        ]
        return {"status": "success", "data": data}
    except Exception:
        return {"status": "success", "data": [], "message": "Could not query history"}
