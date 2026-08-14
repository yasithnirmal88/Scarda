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

## Alert engine — baseline providers (added 2026-08)

The alert engine judges readings against what the plant *should* produce under
current weather, NOT a fixed constant. A cloud/night drop in generation must not
be flagged as a fault. The baseline has three tiers, evaluated in order:

- **Tier 1 (physics):** `WeatherAwareBaselineProvider` (in
  `app/services/alert_engine/baseline_provider.py`) computes expected
  power/current from irradiance + temperature:
  `expected = rated * (irradiance/STC) * (1 + temp_coef*(T-25))`.
  Voltage is nominal in daylight, 0 at night.
- **Tier 2 (historical):** `HistoricalBaselineProvider` queries Scarda's own
  `string_readings` for the median actual power under similar (irradiance,
  temperature) bands via `ReadingRepository.median_power_for_conditions`
  (new method in `app/repositories/reading_repository.py`). When history is
  thin (<5 matches) it degrades to Tier 1; when no weather is supplied it
  degrades to the static baseline. This lets the system self-improve over its
  first ~2 weeks of data without ever being unconfigured.
- **Static fallback:** `StaticBaselineProvider` (fixed 10A/820V/8200W) when
  `weather=None`, so callers that don't supply weather get unchanged behavior.

`main.py::_build_alert_engine` wires the engine with
`HistoricalBaselineProvider` backed by a `ReadingRepository` factory that
returns `None` when the DB is unavailable (graceful degradation to physics).

`OfflineRule` suppresses at night (irradiance below `NIGHT_IRRADIANCE_WPM2`).
Physics params are env-configurable (`THRESHOLD_*` prefix) in
`app/config/thresholds.py`.

The pivotal regression test is `TestCloudTransitionNoFalseAlert` in
`tests/test_alert_engine.py` — a cloud drop must produce zero alerts. The
Tier-2 fallback contract is proven in `tests/test_historical_baseline.py`.

## Test / run

```bash
cd backend
python -m pytest tests/ -v          # 57 tests; alert engine + providers are pure-python
# Backend: uvicorn app.main:app --reload  (needs postgres for DB-backed features)
# With mock: PROVIDER_TYPE=huawei HUAWEI_BASE_URL=http://127.0.0.1:8000
```

Note: `requirements.txt` install can fail building `psycopg2-binary` in minimal
envs — install build deps or skip DB-only tests. Alert-engine tests need only
fastapi/pydantic-settings/apscheduler.

## Deployment

Three independently-deployed pieces; full guide in `docs/DEPLOYMENT.md`.
Frontend → Vercel (Vite, `frontend/vercel.json` SPA rewrites,
`VITE_API_URL` env). Backend → web service + managed Postgres/Timescale.
Mock FusionSolar API (separate repo) → small container host. The agent cannot
provision accounts, databases, or DNS — see the manual-steps section of
`docs/DEPLOYMENT.md`.

## Roadmap (not yet done)

- Live end-to-end validation with the mock running: cycle
  `SIM_SCENARIO` (healthy → degraded → offline → cloudy → healthy) and confirm
  one alert on the right string, debounced, auto-resolves, and **zero** alerts
  on a cloud/weather transition.
- Swap mock for real Huawei Northbound API (set `HUAWEI_BASE_URL` + creds;
  implement real KPI-history polling in `get_historical_readings`/
  `get_historical_weather`).
