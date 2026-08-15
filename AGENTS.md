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

## Live data pipeline (added 2026-08)

The 10-min live + 90-day historical pipeline is wired end-to-end:

- **Mock FusionSolar** (`providers/simulator.py`) emits physics-coupled
  weather + per-string power every `SIM_INTERVAL` (600s). `history/generator.py`
  backfills 90 days of 10-min rows. Exposed via `/plants/{id}/history` and
  `/plants/{id}/weather/history`.
- **Scarda ingestion:** `HuaweiProvider.get_historical_readings` /
  `get_historical_weather` pull the 90-day batch; `history_backfill.py`
  stores both into the existing `string_readings` + `weather_readings`
  hypertables, preserving original measurement timestamps.
- **Composite-id resolution:** provider readings carry ids like
  `SEC01-INV01-STR01`. `HistoricalBaselineProvider` now takes an injectable
  `string_id_resolver` (default `_default_string_id_resolver`) that maps the
  composite id to the integer `strings.id` FK via `resolve_string_id`, so live
  readings are compared against the correct string's history instead of
  falling back to physics.
- **Weather-similarity alerting:** on each live reading,
  `similarity_for_conditions` filters the same string + similar irradiance
  (±100 W/m²) + similar temperature (±3°C) + time-of-day band (±2h) over a
  14-day lookback, requires ≥5 samples, computes median + MAD, and flags an
  outlier. Cloud drops (low power under low irradiance) match history → no
  alert; degraded strings (low power under good irradiance) → anomaly.
- **Frontend:** `useLiveData` hook connects to `/api/ws`, subscribes to
  readings/weather/alerts topics, and a `LiveFeed` dashboard widget renders
  the pushed values. `GET /api/weather/history` returns the stored 10-min
  weather series. No data is fabricated in React.

Integration tests: `tests/test_live_data_flow.py` (5 tests, SQLite-backed)
proves weather backfill timestamps, backfill→similarity, degraded detection,
cloud no-alert, and storage-handler timestamp preservation.

## Roadmap (not yet done)

- Swap mock for real Huawei Northbound API (set `HUAWEI_BASE_URL` + creds;
  implement real KPI-history polling in `get_historical_readings`/
  `get_historical_weather`).

## E2E validation against real TimescaleDB (done 2026-08)

The full pipeline runs against a real TimescaleDB (Docker
`timescale/timescaledb:2.17.2-pg16`) + the mock FusionSolar API:

- 90-day backfill: 518320 readings fetched via `HuaweiProvider`, deduped to
  259160 unique `(string_id, recorded_at)` rows stored in the
  `string_readings` hypertable + 12958 weather rows. Original measurement
  timestamps preserved (range 2026-05-17 → 2026-08-15). Idempotent: a second
  backfill adds 0 rows (ON CONFLICT upsert).
- Historical similarity against real history: 1091 matching samples, median
  51.19 W, MAD 12.38 for a daytime string — query latency ~30–75 ms.
- Alert engine E2E (`scripts/e2e_alert_engine.py`): cloud/low-irradiance
  reading → **normal** (no false alert); degraded string at 40% power under
  good irradiance → **abnormal** (anomaly detected, score 18.7).

Validation scripts: `backend/scripts/e2e_validate.py` (backfill+idempotency+
similarity) and `backend/scripts/e2e_alert_engine.py` (alert scenarios).

### PostgreSQL gotchas fixed (only surface against real Postgres; SQLite tests
masked them)

- **Enum value casing:** `SQLAlchemy`'s `Enum()` stores the member *name*
  (`"OFFLINE"`) by default, but the Postgres enum types are created with the
  member *value* (`"offline"`). Added `enum_values` in `app/utils/enums.py`
  and passed `values_callable=enum_values` on every `Enum(...)` column
  (`inverter`, `string`, `alert`, `user`, `maintenance_log`). Without this,
  any insert against Postgres raised `DataError` on enum value mismatch.
- **Upsert duplicates + param limit:** `ReadingRepository.bulk_create` /
  `WeatherRepository.bulk_create` now (1) dedupe by the conflict key within a
  batch (Postgres rejects `ON CONFLICT DO UPDATE ... affect row a second time`
  when the same key repeats in one statement) and (2) chunk into batches of
  5000 rows to stay under Postgres' 65535 bind-parameter limit.
- **Backfill N+1:** `history_backfill._bulk_store` resolves each *unique*
  composite string id once into a cache (~40 lookups) instead of one
  `coerce_string_id` DB lookup per reading (~500k lookups). `alembic/env.py`
  honors `DATABASE_URL` so migrations run against the compose DB. Migration
  `004_weather_hypertable_and_dedup` makes `weather_readings` a hypertable and
  adds the unique `(string_id, recorded_at)` / `recorded_at` dedup constraints
  the upserts rely on (decompresses chunks first, re-enables compression after).

