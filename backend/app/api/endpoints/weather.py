from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_provider
from app.providers.interfaces import IDataProvider

router = APIRouter()


@router.get("/")
async def get_weather(
    provider: IDataProvider = Depends(get_provider),
):
    weather = await provider.get_weather()
    return {
        "status": "success",
        "data": {
            "temperature_c": weather.get("temperature_c"),
            "humidity_pct": weather.get("humidity_pct"),
            "irradiance_wpm2": weather.get("irradiance_wpm2"),
            "wind_speed_mps": weather.get("wind_speed_mps"),
            "wind_direction": weather.get("wind_direction"),
            "precipitation_mm": weather.get("precipitation_mm"),
            "description": weather.get("description"),
            "timestamp": weather.get("timestamp"),
        },
    }


@router.get("/current")
async def get_current_weather(
    provider: IDataProvider = Depends(get_provider),
):
    weather = await provider.get_weather()
    return {
        "status": "success",
        "data": weather,
    }


@router.get("/history")
async def get_weather_history(
    hours: int = 24,
    request: Request,
):
    """Return the stored 10-min weather time series for the last ``hours``.

    Data originates from the provider (mock-fusionsolar / real Huawei), stored
    in the ``weather_readings`` hypertable with original timestamps. Used by the
    frontend to visualise the live 10-min weather changes.
    """
    from datetime import datetime, timedelta, timezone

    from app.database.migrations import is_database_available

    if not is_database_available():
        return {"status": "success", "data": []}

    try:
        from app.database import get_db
        from app.repositories.weather_repository import WeatherRepository
    except Exception:
        return {"status": "success", "data": []}

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=max(1, min(hours, 24 * 90)))
    try:
        db = next(get_db())
        repo = WeatherRepository(db)
        rows = repo.find_between(start, end)
        return {
            "status": "success",
            "data": [
                {
                    "timestamp": r.recorded_at.isoformat() if r.recorded_at else None,
                    "temperature_c": r.temperature,
                    "humidity_pct": r.humidity,
                    "irradiance_wpm2": r.irradiance,
                    "wind_speed_mps": r.wind_speed,
                    "wind_direction": r.wind_direction,
                    "precipitation_mm": r.precipitation,
                }
                for r in rows
            ],
        }
    except Exception:
        return {"status": "success", "data": []}

