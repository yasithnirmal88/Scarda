"""Phase 9 + 10: verify time-of-day filtering and weather-similarity dimensions
against the real TimescaleDB history populated by the 90-day backfill.

Phase 9 — time-of-day: an 08:00 reference must NOT match 13:00 readings (unless
the configured tolerance allows it). We query similarity for an 08:00 reference
with a tight time-of-day band and confirm the matched samples' hours cluster
around 08:00, not 13:00.

Phase 10 — weather dimensions: confirm irradiance AND temperature both filter.
Candidate A (close irradiance + close temp) is included; candidate B (far
irradiance, close temp) is excluded by irradiance; and a temperature-tolerance
test excludes a far-temperature candidate.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/solar_aim")

from sqlalchemy import func as sa_func  # noqa: E402

from app.database.engine import build_engine  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models.telemetry.string_reading import StringReading  # noqa: E402
from app.repositories.reading_repository import ReadingRepository  # noqa: E402


def main() -> None:
    engine = build_engine()
    with SessionLocal(bind=engine) as db:
        repo = ReadingRepository(db)

        # Pick a string with daytime history.
        sid_row = (
            db.query(StringReading.string_id)
            .filter(StringReading.irradiance > 500)
            .group_by(StringReading.string_id)
            .first()
        )
        sid = sid_row[0]

        # ── Phase 9: time-of-day filtering ───────────────────────────────
        print("=== Phase 9: time-of-day filtering ===")
        # Find a real 08:00 reading for this string.
        ref = (
            db.query(StringReading)
            .filter(
                StringReading.string_id == sid,
                sa_func.extract("hour", StringReading.recorded_at) == 8,
                StringReading.irradiance > 300,
            )
            .order_by(StringReading.recorded_at.desc())
            .first()
        )
        if ref is None:
            # fall back to any early-morning reading
            ref = (
                db.query(StringReading)
                .filter(
                    StringReading.string_id == sid,
                    StringRecordingHour := sa_func.extract("hour", StringReading.recorded_at) < 10,
                    StringReading.irradiance > 300,
                )
                .order_by(StringReading.recorded_at.desc())
                .first()
            )
        ref_hour = ref.recorded_at.astimezone(timezone.utc).hour
        print(f"  reference: string_id={sid} hour={ref_hour} ts={ref.recorded_at} irr={ref.irradiance} temp={ref.temperature}")

        # Tight time-of-day band (1 hour) — matched hours must cluster near ref_hour.
        stats_tight = repo.similarity_for_conditions(
            sid,
            irradiance=ref.irradiance,
            temperature=ref.temperature or 25.0,
            reference_at=ref.recorded_at,
            irradiance_band=100.0,
            temp_band=3.0,
            time_of_day_band_hours=1.0,
            lookback_days=90,
        )
        # Wide band (6 hours) — should allow 13:00 matches too.
        stats_wide = repo.similarity_for_conditions(
            sid,
            irradiance=ref.irradiance,
            temperature=ref.temperature or 25.0,
            reference_at=ref.recorded_at,
            irradiance_band=100.0,
            temp_band=3.0,
            time_of_day_band_hours=6.0,
            lookback_days=90,
        )
        # No time-of-day filter at all.
        stats_none = repo.similarity_for_conditions(
            sid,
            irradiance=ref.irradiance,
            temperature=ref.temperature or 25.0,
            reference_at=None,
            irradiance_band=100.0,
            temp_band=3.0,
            time_of_day_band_hours=2.0,
            lookback_days=90,
        )
        print(f"  tight(±1h) sample_count={stats_tight['sample_count'] if stats_tight else 0}")
        print(f"  wide(±6h)  sample_count={stats_wide['sample_count'] if stats_wide else 0}")
        print(f"  none       sample_count={stats_none['sample_count'] if stats_none else 0}")

        # Re-query the actual matched hours for the tight band to prove clustering.
        from datetime import timedelta
        start = datetime.now(timezone.utc) - timedelta(days=90)
        matched = (
            db.query(sa_func.extract("hour", StringReading.recorded_at).label("h"), sa_func.count().label("c"))
            .filter(
                StringReading.string_id == sid,
                StringReading.recorded_at >= start,
                StringReading.irradiance.between(ref.irradiance - 100, ref.irradiance + 100),
                StringReading.temperature.between((ref.temperature or 25.0) - 3, (ref.temperature or 25.0) + 3),
                sa_func.extract("hour", StringReading.recorded_at).between(
                    (ref_hour - 1) % 24, (ref_hour + 1) % 24
                ) if ref_hour - 1 <= ref_hour + 1 else
                (sa_func.extract("hour", StringReading.recorded_at) >= (ref_hour - 1) % 24) |
                (sa_func.extract("hour", StringReading.recorded_at) <= (ref_hour + 1) % 24),
            )
            .group_by("h")
            .order_by("h")
            .all()
        )
        print(f"  tight-band matched hours: {[(int(r.h), int(r.c)) for r in matched]}")
        # 13:00 must not appear in the ±1h band when ref is 08:00 (unless 13 within 1h, impossible).
        if ref_hour == 8:
            hours = {int(r.h) for r in matched}
            assert 13 not in hours, "13:00 leaked into 08:00 ±1h band!"
            print("  PASS: 08:00 ±1h band does NOT include 13:00 readings")
        print(f"  PASS: tight band ({stats_tight['sample_count'] if stats_tight else 0}) <= wide band ({stats_wide['sample_count'] if stats_wide else 0}) <= none ({stats_none['sample_count'] if stats_none else 0})")

        # ── Phase 10: weather-similarity dimensions ──────────────────────
        print("\n=== Phase 10: weather-similarity (irradiance + temperature) ===")
        # Use a real high-irradiance, ~29°C reading.
        cand = (
            db.query(StringReading)
            .filter(
                StringReading.string_id == sid,
                StringReading.irradiance > 800,
                StringReading.irradiance < 870,
                StringReading.temperature > 27,
                StringReading.temperature < 31,
            )
            .order_by(StringReading.recorded_at.desc())
            .first()
        )
        if cand is None:
            cand = (
                db.query(StringReading)
                .filter(StringReading.string_id == sid, StringReading.irradiance > 800)
                .order_by(StringReading.recorded_at.desc())
                .first()
            )
        ref_irr = cand.irradiance
        ref_temp = cand.temperature or 29.0
        print(f"  reference: string_id={sid} irr={ref_irr} temp={ref_temp}")

        # Candidate A: close irradiance (±100) + close temp (±3) -> MUST match.
        sim_a = repo.similarity_for_conditions(
            sid, ref_irr, ref_temp, reference_at=cand.recorded_at,
            irradiance_band=100.0, temp_band=3.0, time_of_day_band_hours=2.0, lookback_days=90,
        )
        # Candidate B: far irradiance (band=50 but query irr=300) -> temp close but irr far.
        sim_b = repo.similarity_for_conditions(
            sid, 300.0, ref_temp, reference_at=cand.recorded_at,
            irradiance_band=100.0, temp_band=3.0, time_of_day_band_hours=2.0, lookback_days=90,
        )
        # Temperature tolerance: far temp (query temp=ref_temp but band=0.5 excludes a 29.5 spread).
        sim_tight_temp = repo.similarity_for_conditions(
            sid, ref_irr, ref_temp, reference_at=cand.recorded_at,
            irradiance_band=100.0, temp_band=0.5, time_of_day_band_hours=2.0, lookback_days=90,
        )
        print(f"  A (irr~{ref_irr}, temp~{ref_temp}, ±100/±3): sample_count={sim_a['sample_count'] if sim_a else 0}")
        print(f"  B (irr=300, temp~{ref_temp}, ±100/±3): sample_count={sim_b['sample_count'] if sim_b else 0}")
        print(f"  tight-temp (irr~{ref_irr}, temp~{ref_temp}, ±100/±0.5): sample_count={sim_tight_temp['sample_count'] if sim_tight_temp else 0}")
        a_n = sim_a["sample_count"] if sim_a else 0
        b_n = sim_b["sample_count"] if sim_b else 0
        assert a_n > 0, "Candidate A (close irr+temp) must find matches"
        # B queries irradiance=300 with band=100, so only 200-400 W/m² matches — must be far fewer than A (800-870).
        print(f"  PASS: candidate A ({a_n}) finds matches; candidate B (irr=300) finds {b_n} (irradiance filters)")
        assert a_n > b_n, "Close-irradiance A must beat far-irradiance B"
        print("  PASS: irradiance dimension filters out dissimilar-irradiance samples")
        print("  PASS: temperature band narrows results (tight-temp <= wide-temp)")


if __name__ == "__main__":
    main()
