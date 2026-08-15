"""Integration tests for the live 10-min data flow.

Verifies the end-to-end pipeline the user requires:

    mock provider (weather + power, 10-min, original timestamps)
        → HuaweiProvider-shaped data
        → history_backfill stores into string_readings + weather_readings
        → ReadingStorageHandler preserves original timestamps
        → HistoricalBaselineProvider similarity query finds matching history
        → a degraded string under similar weather is flagged abnormal
        → a cloud drop (weather-driven) is NOT flagged

Uses an in-memory SQLite session so no Postgres is required.
"""

from __future__ import annotations

import os

# Force SQLite before any app.database import so the module-level engine
# builds against SQLite (no psycopg2 needed).
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import StringReading, WeatherReading  # noqa: F401  (register tables)


@pytest.fixture()
def db_session():
    """In-memory SQLite session with all tables created directly.

    SQLite cannot autoincrement on a composite primary key (which the real
    Postgres ``string_readings`` hypertable uses), so the ``string_readings``
    table is created with raw DDL where ``id`` is a plain integer and the
    application assigns ids. This lets the full storage + similarity pipeline
    run without Postgres.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    # Create every table except string_readings via metadata, then add the
    # composite-PK string_readings manually.
    from app.models.telemetry.string_reading import StringReading

    StringReading.__table__  # ensure registered
    Base.metadata.create_all(
        engine,
        tables=[
            t for t in Base.metadata.sorted_tables if t.name != "string_readings"
        ],
    )
    with engine.begin() as conn:
        from sqlalchemy import text

        conn.execute(
            text(
                "CREATE TABLE string_readings ("
                "id INTEGER NOT NULL, "
                "string_id INTEGER NOT NULL REFERENCES strings(id), "
                "recorded_at DATETIME NOT NULL, "
                "voltage FLOAT, current FLOAT, power FLOAT, "
                "temperature FLOAT, irradiance FLOAT, "
                "PRIMARY KEY (id, recorded_at))"
            )
        )
    # Auto-assign string_readings.id on insert (SQLite can't autoincrement a
    # composite PK; real Postgres/TimescaleDB does).
    from sqlalchemy import event, select, func

    _counter = {"n": 0}

    @event.listens_for(StringReading, "before_insert")
    def _assign_id(mapper, connection, target):
        if target.id is None:
            max_id = connection.execute(
                select(func.max(StringReading.id))
            ).scalar() or 0
            target.id = max_id + 1

    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    event.remove(StringReading, "before_insert", _assign_id)


# --- Weather backfill -------------------------------------------------------


def test_weather_backfill_stores_10min_series_with_original_timestamps(db_session) -> None:
    """The 90-day, 10-min weather series must land in weather_readings with
    each sample keeping its original measurement timestamp (not insertion time)."""
    from app.services.history_backfill import _bulk_store_weather

    start = datetime(2026, 8, 14, 0, 0, tzinfo=timezone.utc)
    points = [
        {
            "timestamp": (start + timedelta(minutes=i * 10)).isoformat(),
            "temperature_c": 20.0 + i * 0.1,
            "irradiance_wpm2": float(i * 30),
            "humidity_pct": 0.0,
            "wind_speed_mps": 0.0,
            "wind_direction": "N/A",
            "precipitation_mm": 0.0,
        }
        for i in range(6)
    ]
    stored = _bulk_store_weather(db_session, points)
    assert stored == 6
    rows = db_session.query(WeatherReading).order_by(WeatherReading.recorded_at).all()
    assert len(rows) == 6
    # Original timestamps preserved (not collapsed to one insertion time).
    # SQLite stores naive datetimes; compare the instant.
    assert rows[0].recorded_at.replace(tzinfo=None) == start.replace(tzinfo=None)
    assert rows[-1].recorded_at.replace(tzinfo=None) == (start + timedelta(minutes=50)).replace(tzinfo=None)
    assert rows[3].irradiance == 90.0


# --- Reading backfill + similarity ------------------------------------------


def _make_readings(start: datetime, count: int, power_fn) -> list[dict]:
    """Build ``count`` 10-min readings for one string with given power."""
    out = []
    for i in range(count):
        t = start + timedelta(minutes=i * 10)
        out.append(
            {
                "string_id": "SEC01-INV01-STR01",
                "inverter_id": "SEC01-INV01",
                "timestamp": t.isoformat(),
                "current_a": power_fn(i) / 600.0,
                "voltage_v": 600.0,
                "power_w": power_fn(i),
                "irradiance_wpm2": 820.0,
                "temperature_c": 29.0,
                "status": "ok",
            }
        )
    return out


def test_backfill_stores_readings_then_similarity_finds_them(db_session) -> None:
    """Backfilled history must be queryable by the similarity method, proving
    the 90-day 10-min rows are usable for baseline comparison."""
    from app.services.history_backfill import _bulk_store
    from app.repositories.reading_repository import ReadingRepository

    start = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
    readings = _make_readings(start, 20, lambda i: 4200.0)
    stored = _bulk_store(db_session, readings)
    assert stored == 20

    repo = ReadingRepository(db_session)
    # The string FK was lazily created during backfill (coerce_string_id).
    from app.models import String
    string = db_session.query(String).filter_by(code="STR01").first()
    assert string is not None

    stats = repo.similarity_for_conditions(
        string.id,
        irradiance=820.0,
        temperature=29.0,
        reference_at=datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc),
        irradiance_band=100.0,
        temp_band=3.0,
        time_of_day_band_hours=2.0,
        lookback_days=30,
        min_samples=5,
    )
    assert stats is not None
    assert stats["sample_count"] >= 5
    assert stats["median_power"] == pytest.approx(4200.0, rel=1e-2)


def test_degraded_string_detected_against_history(db_session) -> None:
    """A current reading far below the historical median under similar weather
    is flagged abnormal by the baseline provider's explain_reading."""
    from app.services.alert_engine.baseline_provider import HistoricalBaselineProvider
    from app.services.alert_engine.config import AlertEngineConfig
    from app.services.history_backfill import _bulk_store
    from app.repositories.reading_repository import ReadingRepository

    start = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
    # 20 healthy historical points at ~4.2 kW under 820 W/m², 29°C.
    _bulk_store(db_session, _make_readings(start, 20, lambda i: 4200.0))

    cfg = AlertEngineConfig()
    provider = HistoricalBaselineProvider(
        config=cfg,
        reading_repo_factory=lambda: ReadingRepository(db_session),
    )
    # A current degraded reading: 1.8 kW under the same weather.
    result = provider.explain_reading(
        "SEC01-INV01-STR01",
        power=1800.0,
        weather={"irradiance": 820.0, "ambient_temperature": 29.0},
        measured_at=datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc),
    )
    assert result["method"] == "historical_similarity"
    assert result["status"] == "abnormal"
    assert result["expected_power"] == pytest.approx(4200.0, rel=1e-2)
    assert result["deviation"] < 0


def test_cloud_drop_not_flagged_against_history(db_session) -> None:
    """When the current low power matches what the string historically produced
    under similarly low irradiance, it is normal (no false alert)."""
    from app.services.alert_engine.baseline_provider import HistoricalBaselineProvider
    from app.services.alert_engine.config import AlertEngineConfig
    from app.services.history_backfill import _bulk_store
    from app.repositories.reading_repository import ReadingRepository

    start = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
    # History under cloudy conditions: ~2.1 kW at 400 W/m².
    cloudy = []
    for i in range(20):
        t = start + timedelta(minutes=i * 10)
        cloudy.append(
            {
                "string_id": "SEC01-INV01-STR01",
                "inverter_id": "SEC01-INV01",
                "timestamp": t.isoformat(),
                "current_a": 3.5,
                "voltage_v": 600.0,
                "power_w": 2100.0,
                "irradiance_wpm2": 400.0,
                "temperature_c": 27.0,
                "status": "ok",
            }
        )
    _bulk_store(db_session, cloudy)

    cfg = AlertEngineConfig()
    provider = HistoricalBaselineProvider(
        config=cfg,
        reading_repo_factory=lambda: ReadingRepository(db_session),
    )
    # Current cloud reading: 2.1 kW at 400 W/m² → matches history → normal.
    result = provider.explain_reading(
        "SEC01-INV01-STR01",
        power=2100.0,
        weather={"irradiance": 400.0, "ambient_temperature": 27.0},
        measured_at=datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc),
    )
    assert result["method"] == "historical_similarity"
    assert result["status"] == "normal"
    assert result["expected_power"] == pytest.approx(2100.0, rel=1e-2)


def test_live_reading_timestamp_preserved_by_storage_handler(db_session) -> None:
    """The storage handler must keep the source measurement timestamp, not the
    ingestion time, so historical analysis uses real measurement times."""
    from app.events.event_bus import EventBus
    from app.events.events import ReadingGenerated
    from app.events.handlers import ReadingStorageHandler

    # Monkeypatch the DB availability check + get_db to use our in-memory session.
    from app.database import migrations as mig

    orig_available = mig.is_database_available
    mig._CREATED = True
    from app.database import session as session_mod

    orig_get_db = getattr(session_mod, "get_db", None)
    session_mod.get_db = lambda: iter([db_session])
    try:
        from app.database import get_db as get_db_top

        orig_top = get_db_top
        import app.database as db_mod

        db_mod.get_db = lambda: iter([db_session])

        bus = EventBus()
        handler = ReadingStorageHandler(db_session, bus)
        measured = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
        await_bus = []

        async def capture(event):
            await_bus.append(event)

        bus.subscribe("reading.stored", capture)

        import asyncio

        asyncio.run(
            handler.handle(
                ReadingGenerated(
                    readings=[
                        {
                            "string_id": "SEC01-INV01-STR01",
                            "voltage_v": 600.0,
                            "current_a": 7.0,
                            "power_w": 4200.0,
                            "irradiance_wpm2": 820.0,
                            "temperature_c": 29.0,
                            "timestamp": measured.isoformat(),
                        }
                    ],
                    weather={
                        "temperature_c": 29.0,
                        "irradiance_wpm2": 820.0,
                        "timestamp": measured.isoformat(),
                    },
                )
            )
        )

        row = db_session.query(StringReading).first()
        assert row is not None
        # Original timestamp preserved (SQLite stores naive datetimes).
        assert row.recorded_at.replace(tzinfo=None) == measured.replace(tzinfo=None)
        assert row.power == 4200.0
    finally:
        mig._CREATED = orig_available()
        if orig_get_db is not None:
            session_mod.get_db = orig_get_db
        if orig_top is not None:
            import app.database as db_mod2

            db_mod2.get_db = orig_top
