"""End-to-end validation against real PostgreSQL + TimescaleDB.

Runs the full production path:

    Mock FusionSolar API
        -> HuaweiProvider (get_historical_readings / get_historical_weather)
        -> history_backfill
        -> TimescaleDB (string_readings / weather_readings)

then verifies the stored rows, original timestamps, idempotency, and the
historical-similarity baseline against real DB records.

This is a validation script, NOT a unit test. It requires a running
TimescaleDB (DATABASE_URL) and a running Mock FusionSolar API (HUAWEI_BASE_URL).
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone

# Configure provider + DB before importing app modules that read settings.
os.environ.setdefault("PROVIDER_TYPE", "huawei")
os.environ.setdefault("HUAWEI_BASE_URL", "http://127.0.0.1:8001")
os.environ.setdefault("HUAWEI_USERNAME", "huawei")
os.environ.setdefault("HUAWEI_PASSWORD", "huawei")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/solar_aim"
)

from app.database.engine import build_engine  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.providers import create_provider  # noqa: E402
from app.services.history_backfill import backfill_history  # noqa: E402
from app.repositories.reading_repository import ReadingRepository  # noqa: E402
from app.models.telemetry.string_reading import StringReading  # noqa: E402
from app.models.telemetry.weather_reading import WeatherReading  # noqa: E402


def _count(db, model) -> int:
    return db.query(model).count()


def _minmax(db, model):
    row = db.query(model.recorded_at).order_by(model.recorded_at).first()
    last = db.query(model.recorded_at).order_by(model.recorded_at.desc()).first()
    return row[0] if row else None, last[0] if last else None


async def main() -> None:
    print("=== E2E: provider -> backfill -> TimescaleDB ===")
    provider = create_provider()
    print("provider:", await provider.health_check())

    engine = build_engine()

    # --- First backfill (90 days) ---
    with SessionLocal(bind=engine) as db:
        before_r = _count(db, StringReading)
        before_w = _count(db, WeatherReading)
        print(f"before: readings={before_r} weather={before_w}")

    with SessionLocal(bind=engine) as db:
        stored = await backfill_history(provider, days=90, db_session=db)
    print(f"backfill returned: {stored}")

    with SessionLocal(bind=engine) as db:
        r1 = _count(db, StringReading)
        w1 = _count(db, WeatherReading)
        rmin, rmax = _minmax(db, StringReading)
        wmin, wmax = _minmax(db, WeatherReading)
        distinct_strings = db.query(StringReading.string_id).distinct().count()
        print(f"after 1st backfill: readings={r1} weather={w1}")
        print(f"  readings range: {rmin} -> {rmax}")
        print(f"  weather range:   {wmin} -> {wmax}")
        print(f"  distinct string_id: {distinct_strings}")

    # --- Idempotency: second backfill must not duplicate ---
    with SessionLocal(bind=engine) as db:
        await backfill_history(provider, days=90, db_session=db)
    with SessionLocal(bind=engine) as db:
        r2 = _count(db, StringReading)
        w2 = _count(db, WeatherReading)
        print(f"after 2nd backfill: readings={r2} weather={w2}")
        assert r2 == r1, f"NOT idempotent: readings {r1} -> {r2}"
        assert w2 == w1, f"NOT idempotent: weather {w1} -> {w2}"
        print("IDEMPOTENT: second backfill did not duplicate rows OK")

    # --- Similarity against real DB ---
    with SessionLocal(bind=engine) as db:
        repo = ReadingRepository(db)
        sid_row = (
            db.query(StringReading.string_id)
            .filter(StringReading.irradiance > 200)
            .first()
        )
        if sid_row:
            sid = sid_row[0]
            ref_row = (
                db.query(StringReading)
                .filter(
                    StringReading.string_id == sid,
                    StringReading.irradiance > 200,
                )
                .order_by(StringReading.recorded_at.desc())
                .first()
            )
            stats = repo.similarity_for_conditions(
                sid,
                irradiance=ref_row.irradiance,
                temperature=ref_row.temperature or 25.0,
                reference_at=ref_row.recorded_at,
                lookback_days=90,
            )
            print("=== similarity (real DB, healthy pick) ===")
            print(f"  string_id={sid} ts={ref_row.recorded_at}")
            print(f"  actual_power={ref_row.power} irradiance={ref_row.irradiance} temp={ref_row.temperature}")
            print(f"  stats={stats}")
        else:
            print("no daytime readings found for similarity test")


if __name__ == "__main__":
    asyncio.run(main())
