"""Alert-engine E2E against real TimescaleDB history.

Validates the two pivotal acceptance scenarios using the *real* 90-day history
already stored by e2e_validate.py:

  Cloud transition: a reading whose power dropped because irradiance dropped
  must NOT be flagged abnormal — the historical median under similar (low)
  irradiance tracks the lower actual power.

  Degraded string: a reading with normal irradiance/temperature but abnormally
  low power MUST be flagged abnormal — it deviates strongly from the historical
  median under those conditions.

Requires a populated TimescaleDB (run e2e_validate.py first) + running mock.
"""
from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone

os.environ.setdefault("PROVIDER_TYPE", "huawei")
os.environ.setdefault("HUAWEI_BASE_URL", "http://127.0.0.1:8001")
os.environ.setdefault("HUAWEI_USERNAME", "huawei")
os.environ.setdefault("HUAWEI_PASSWORD", "huawei")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/solar_aim"
)

from app.database.engine import build_engine  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models.telemetry.string_reading import StringReading  # noqa: E402
from app.repositories.reading_repository import ReadingRepository  # noqa: E402
from app.services.alert_engine.baseline_provider import (  # noqa: E402
    HistoricalBaselineProvider,
)
from sqlalchemy import func as sa_func  # noqa: E402


def _engine():
    return build_engine()


def _pick_two_conditions(engine):
    """Find one high-irradiance and one low-irradiance daytime reading.

    Uses the real stored history. Returns (string_int_id, composite_id, high,
    low) where high/low are StringReading rows with very different irradiance
    but the same string.
    """
    with SessionLocal(bind=engine) as db:
        # a string with plenty of history (use MAX(id) as a stable proxy — can't
        # ORDER BY id with GROUP BY under strict Postgres).
        sid_row = (
            db.query(StringReading.string_id, sa_func.max(StringReading.id).label("mx"))
            .group_by(StringReading.string_id)
            .order_by(sa_func.max(StringReading.id).desc())
            .first()
        )
        sid = sid_row[0]
        # high irradiance midday reading
        high = (
            db.query(StringReading)
            .filter(StringReading.string_id == sid, StringReading.irradiance > 600)
            .order_by(StringReading.irradiance.desc())
            .first()
        )
        # low irradiance reading (cloudy / late afternoon) same string
        low = (
            db.query(StringReading)
            .filter(
                StringReading.string_id == sid,
                StringReading.irradiance < 300,
                StringReading.irradiance > 80,
            )
            .order_by(StringReading.irradiance.asc())
            .first()
        )
        # map int id back to the full composite Scarda id (SEC01-INV01-STR08)
        # the provider/alert-engine uses, by walking the section/inverter/string
        # hierarchy.
        from app.models.master.inverter import Inverter  # noqa: E402
        from app.models.master.section import Section  # noqa: E402
        from app.models.master.string import String  # noqa: E402

        s = db.query(String).filter(String.id == sid).first()
        inv = db.query(Inverter).filter(Inverter.id == s.inverter_id).first()
        sec = db.query(Section).filter(Section.id == inv.section_id).first()
        composite = f"{sec.code}-{inv.code}-{s.code}"
        return sid, composite, high, low


async def main() -> None:
    engine = _engine()
    sid, composite, high, low = _pick_two_conditions(engine)
    print(f"string int_id={sid} composite={composite}")
    print(f"  high-irr reading: irr={high.irradiance} temp={high.temperature} power={high.power} @ {high.recorded_at}")
    print(f"  low-irr  reading: irr={low.irradiance} temp={low.temperature} power={low.power} @ {low.recorded_at}")

    def repo_factory():
        return ReadingRepository(SessionLocal(bind=engine))

    provider = HistoricalBaselineProvider(reading_repo_factory=repo_factory)

    # ── Scenario A: cloud transition (low irradiance, but historically-consistent power)
    # Use the actual low reading's power, which the history shows is normal for
    # that irradiance -> must be NORMAL (no false alert).
    t0 = time.perf_counter()
    explain_low = provider.explain_reading(
        composite,
        power=low.power,
        weather={"irradiance": low.irradiance, "ambient_temperature": low.temperature},
        measured_at=low.recorded_at,
    )
    dt = time.perf_counter() - t0
    print("\n=== Scenario A: cloud/low-irradiance reading ===")
    for k in ("current_power", "expected_power", "irradiance", "temperature",
              "historical_sample_count", "historical_median_power",
              "deviation_pct", "anomaly_score", "status"):
        print(f"  {k}: {explain_low.get(k)}")
    print(f"  similarity query latency: {dt*1000:.1f} ms")
    assert explain_low["status"] == "normal", "CLOUD TRANSITION MUST NOT ALERT"
    print("  PASS: cloud transition -> no false alert")

    # ── Scenario B: degraded string (normal irradiance, abnormally low power)
    # Take the high-irradiance conditions but report a power far below the
    # historical median -> must be ABNORMAL.
    degraded_power = high.power * 0.4
    t0 = time.perf_counter()
    explain_deg = provider.explain_reading(
        composite,
        power=degraded_power,
        weather={"irradiance": high.irradiance, "ambient_temperature": high.temperature},
        measured_at=high.recorded_at,
    )
    dt = time.perf_counter() - t0
    print("\n=== Scenario B: degraded string (same weather, 40% power) ===")
    for k in ("current_power", "expected_power", "irradiance", "temperature",
              "historical_sample_count", "historical_median_power",
              "deviation", "deviation_pct", "anomaly_score", "status"):
        print(f"  {k}: {explain_deg.get(k)}")
    print(f"  similarity query latency: {dt*1000:.1f} ms")
    assert explain_deg["status"] == "abnormal", "DEGRADED STRING MUST ALERT"
    print("  PASS: degraded string -> anomaly detected")

    print("\nALL ALERT-ENGINE E2E SCENARIOS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
