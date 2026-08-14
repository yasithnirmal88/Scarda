# Scarda (Solar AIM) — Agent Notes

## Architecture

Two-system design (do NOT merge):
- **Mock FusionSolar API** (separate project) = upstream solar-data source. Simulates
  physics (irradiance, temperature, faults). Knows nothing about alerts/baselines.
- **Scarda** = monitoring brain. Owns history, baselines, comparison, alerts, UI.
  Talks to the data source via `IDataProvider` → `HuaweiProvider` (swap mock for real
  Huawei later by changing `PROVIDER_TYPE=huawei` + `HUAWEI_BASE_URL`).

Data flow: provider → scheduler tick → EventBus(`reading.generated` → `stored` →
`alert`) → telemetry storage + alert engine + WebSocket broadcast.

## Alert engine — weather-aware baseline (added 2026-08)

The alert engine judges readings against what the plant *should* produce under
current weather, NOT a fixed constant. A cloud/night drop in generation must not
be flagged as a fault.

- `WeatherAwareBaselineProvider` (in `app/services/alert_engine/baseline_provider.py`)
  computes expected power/current from irradiance + temperature:
  `expected = rated * (irradiance/STC) * (1 + temp_coef*(T-25))`.
  Voltage is nominal in daylight, 0 at night.
- Falls back to `StaticBaselineProvider` (fixed 10A/820V/8200W) when `weather=None`,
  so callers that don't supply weather get unchanged behavior.
- `OfflineRule` suppresses at night (irradiance below `NIGHT_IRRADIANCE_WPM2`).
- Physics params are env-configurable (`THRESHOLD_*` prefix) in `app/config/thresholds.py`.

The pivotal regression test is `TestCloudTransitionNoFalseAlert` in
`tests/test_alert_engine.py` — a cloud drop must produce zero alerts.

## Test / run

```bash
cd backend
python -m pytest tests/ -v          # 49 tests; does NOT need psycopg2 (alert engine is pure-python)
# Backend: uvicorn app.main:app --reload  (needs postgres for DB-backed features)
# With mock: PROVIDER_TYPE=huawei HUAWEI_BASE_URL=http://127.0.0.1:8000
```

Note: `requirements.txt` install can fail building `psycopg2-binary` in minimal
envs — install build deps or skip DB-only tests. Alert-engine tests need only
fastapi/pydantic-settings/apscheduler.

## Roadmap (not yet done)

- Step 3: `HistoricalBaselineProvider` (Tier 2) — query stored history for the
  median actual power under similar (irradiance, temperature) bands; fall back
  to the physics model when history is thin (<5 points). Home:
  `app/services/telemetry/statistics.py` + a new `median_power_for_conditions`
  on `ReadingRepository` (the `StringReading` model already stores irradiance/temp).
- Step 4: deploy mock / backend+Timescale / frontend-on-Vercel separately.
