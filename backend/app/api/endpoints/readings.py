from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_provider
from app.database import get_db
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


@router.get("/anomaly-explanation/{string_id}")
async def get_anomaly_explanation(string_id: str, request: Request):
    """Explain why a reading was/was not flagged as an anomaly.

    Returns the full historical-similarity explanation computed by the
    ``HistoricalBaselineProvider``: current vs expected power, irradiance,
    temperature, historical sample count, historical median + MAD, deviation,
    anomaly score, and a status string. The frontend renders this directly —
    it never computes expected power itself.

    Uses the latest stored reading for the string (falls back to the live
    provider snapshot when no DB is available).
    """
    from app.services.alert_engine.baseline_provider import (
        HistoricalBaselineProvider,
        WeatherAwareBaselineProvider,
    )
    from app.services.alert_engine.config import AlertEngineConfig

    cfg = AlertEngineConfig()
    physics = WeatherAwareBaselineProvider(cfg)

    def _repo_factory():
        try:
            session = next(get_db())
            from app.repositories.reading_repository import ReadingRepository

            return ReadingRepository(session)
        except Exception:
            return None

    provider_hist = HistoricalBaselineProvider(
        config=cfg, reading_repo_factory=_repo_factory, physics_provider=physics
    )

    # Resolve the integer string FK (needed for the historical query) from the
    # composite Scarda id, then use the latest stored reading for that string.
    numeric_sid: int | None = None
    measured_at = None
    try:
        from app.providers.huawei.string_identity import coerce_string_id

        session = next(get_db())
        numeric_sid = coerce_string_id(session, string_id)
        if numeric_sid and numeric_sid != 0:
            from app.repositories.reading_repository import ReadingRepository

            latest = ReadingRepository(session).find_by_string(numeric_sid)[-1:]
            if latest:
                rec = latest[0]
                measured_at = rec.recorded_at
                power = float(rec.power or 0.0)
                weather = {
                    "irradiance": float(rec.irradiance or 0.0),
                    "ambient_temperature": float(rec.temperature or 25.0),
                }
                return provider_hist.explain_reading(
                    str(numeric_sid), power, weather, measured_at
                )
    except Exception:
        pass

    # Fallback: live provider snapshot for this string.
    try:
        provider = getattr(request.app.state, "provider", None)
        if provider is not None:
            snap = await provider.get_current_readings()
            for rd in snap.get("readings", []):
                rd_sid = str(rd.get("string_id"))
                if rd_sid == str(string_id) or rd_sid.endswith(str(string_id)):
                    power = float(rd.get("power_w") or rd.get("power") or 0.0)
                    weather = {
                        "irradiance": float(
                            rd.get("irradiance_wpm2") or rd.get("irradiance") or 0.0
                        ),
                        "ambient_temperature": float(
                            rd.get("temperature_c") or rd.get("temperature") or 25.0
                        ),
                    }
                    ts = rd.get("timestamp")
                    if ts:
                        try:
                            from datetime import datetime

                            measured_at = datetime.fromisoformat(
                                str(ts).replace("Z", "+00:00")
                            )
                        except (TypeError, ValueError):
                            measured_at = None
                    return provider_hist.explain_reading(
                        str(numeric_sid or string_id), power, weather, measured_at
                    )
    except Exception:
        pass

    return {
        "string_id": string_id,
        "status": "unavailable",
        "message": "No reading available to explain",
    }


@router.get("/similarity")
async def get_similarity_params():
    """Return the configured historical-similarity tolerances.

    Lets the frontend/admin show the active algorithm parameters (irradiance
    band, temperature band, time-of-day band, lookback window, min samples, MAD
    multiplier) without hardcoding them.
    """
    from app.services.alert_engine.config import AlertEngineConfig

    cfg = AlertEngineConfig()
    return {
        "irradiance_band_wpm2": cfg.historical_irradiance_band,
        "temperature_band_c": cfg.historical_temp_band,
        "time_of_day_band_hours": cfg.historical_time_of_day_band_hours,
        "lookback_days": cfg.historical_lookback_days,
        "min_samples": cfg.historical_min_samples,
        "mad_multiplier": cfg.historical_mad_multiplier,
        "algorithm": "median + MAD historical similarity (same string, similar irradiance/temperature/time-of-day)",
    }
