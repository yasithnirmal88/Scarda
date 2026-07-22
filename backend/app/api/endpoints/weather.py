from __future__ import annotations

from fastapi import APIRouter, Depends

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
