# Deployment Guide

Scarda is deployed as three independently-managed pieces that mirror the
architecture:

```
Mock FusionSolar API  (data source) -> Scarda Backend (monitoring brain) -> Scarda Frontend (Vercel)
```

This document covers the code-side configuration that is already in place
and the manual steps that must be performed by a human on the hosting
providers.

---

## What is already wired (code-side)

| Concern | Where | Notes |
|---|---|---|
| Provider abstraction | `backend/app/providers/` | Swap mock for real Huawei by setting `PROVIDER_TYPE=huawei` + `HUAWEI_BASE_URL`. No code changes. |
| Weather-aware + historical baseline | `backend/app/services/alert_engine/baseline_provider.py` | `HistoricalBaselineProvider` reads from Scarda's own DB and falls back to the physics model, then the static baseline. |
| Scheduler in-process | `backend/app/main.py` | APScheduler runs in the same process; no separate worker needed. |
| Frontend SPA routing | `frontend/vercel.json` | Rewrites non-`/api` paths to `/index.html`. |
| Frontend API base URL | `frontend/src/utils/constants.ts` | `import.meta.env.VITE_API_URL \|\| '/api'` — set `VITE_API_URL` to the backend's public URL. |
| Frontend Dockerfile | `infrastructure/docker/frontend.Dockerfile` | nginx config inlined; no longer depends on `infrastructure/nginx/` being in the build context. |
| Timescale-ready schema | `backend/alembic/versions/003_convert_string_readings_hypertable.py` | `string_readings` is a hypertable. |

---

## Deployment order

Deploy in this order so each piece can be validated against the one before it.

### 1. Mock FusionSolar API (data source)

This is a separate project (not in this repo). It is a FastAPI app that
simulates a solar plant.

- **Host**: any small always-on container host (Render, Fly.io, Railway, or a
  VPS). In-memory state is acceptable for a dev simulator.
- **Containerize**: reuse the FastAPI Docker pattern from
  `infrastructure/docker/backend.Dockerfile`.
- **Env**: set `SIM_SCENARIO`, `SIM_INVERTERS`, `SIM_STRINGS_PER_INVERTER`,
  `SIM_INTERVAL` per the mock project's config.
- **Validate**: `GET https://<mock-host>/api/health` returns 200 and
  `GET https://<mock-host>/api/plants/sim-plant-001` returns plant data.

### 2. Scarda Backend (monitoring brain)

- **Host**: a web service that does not sleep (scheduler ticks must be
  reliable). Render, Fly.io, or Railway web services all work.
- **Database**: managed TimescaleDB (recommended) or PostgreSQL with the
  Timescale extension. The hypertable migration for `string_readings` enables
  time-series compression + retention, which matters once you store
  864 strings × every-5-min × months.
- **Env vars** (set in the host dashboard, not committed):
  - `PROVIDER_TYPE=huawei`
  - `HUAWEI_BASE_URL=https://<mock-host>`  (the mock from step 1)
  - `HUAWEI_USERNAME`, `HUAWEI_PASSWORD`, `HUAWEI_PLANT_ID=sim-plant-001`
  - `DATABASE_URL=postgresql+psycopg2://<user>:<pass>@<db-host>/<db>`
  - `SECRET_KEY=<generate-a-strong-random-value>`  (JWT signing)
  - `SCHEDULER_ENABLED=true`
  - Threshold / physics params from `.env.example` as needed
- **Validate**:
  - `GET https://<backend-host>/api/scheduler/jobs` shows scheduled jobs.
  - The DB `string_readings` table accumulates rows every simulator interval.
  - `GET https://<backend-host>/` returns `{"status": "running"}`.

### 3. Scarda Frontend (Vercel)

- **Build**: Vercel builds the Vite app directly from `npm run build`; no
  Docker needed.
- **Framework preset**: Vite (auto-detected from `vite.config.ts`).
- **Root directory**: `frontend` (if the Vercel project root is the repo
  root, set this in Project Settings).
- **Env var** (set in Vercel Project Settings → Environment Variables):
  - `VITE_API_URL=https://<backend-host>/api`  (absolute URL to the backend)
- **SPA routing**: `frontend/vercel.json` rewrites all non-`/api` paths to
  `/index.html` so client-side routes (`/alerts`, `/dashboard`, ...) work.
- **Deployment Protection**: if you enable Vercel Deployment Protection on
  preview URLs, set up a Protection Bypass secret for any automated
  testing/agent access. For production, protection is not required.
- **Validate**: log in, confirm the dashboard populates from the backend,
  and that client-side navigation (e.g. `/alerts`) does not 404 on refresh.

---

## Post-deployment end-to-end validation

Run this once the three pieces are live and connected:

1. **Healthy baseline**: mock `SIM_SCENARIO=healthy`. After 2 confirmation
   cycles, confirm zero alerts in the frontend.
2. **Degraded string**: mock `SIM_SCENARIO=degraded_string`. Confirm exactly
   one alert appears on the affected string (after the confirmation delay),
   pushed in real time via WebSocket.
3. **Offline inverter**: mock `SIM_SCENARIO=offline_inverter`. Confirm a
   `communication_failure` / `offline` alert, and that it does not spam (the
   confirmation engine debounces).
4. **Recovery**: set `SIM_SCENARIO=healthy` again. Confirm the active alert
   auto-resolves.
5. **Cloud / weather transition (pivotal)**: drive an irradiance drop on the
   mock (a "cloudy" weather mode). Confirm **no** false alert — the
   weather-aware baseline reduces the expected output alongside the actual.
   This is the test that proves the core contract in production.

If your mock cannot vary weather dynamically, add a "cloudy" weather mode to
the mock first; it is required to validate case 5.

---

## Manual steps the agent cannot perform

These require accounts, billing, and secrets only a human can provision:

1. **Create accounts** on Vercel, the backend host, and the database provider.
2. **Provision managed TimescaleDB / Postgres** and obtain the connection
   string. Run `alembic upgrade head` against it (or let the backend do it via
   `init_database()` on first boot — verify the env is set).
3. **Generate a strong `SECRET_KEY`** for JWT and set it as a backend env var.
4. **Deploy the Mock FusionSolar API** (separate repo) to a public URL.
5. **Set the backend env vars** (listed in step 2 above) in the host dashboard.
6. **Create the Vercel project**, point it at the `frontend` directory, and set
   `VITE_API_URL` in Vercel Project Settings → Environment Variables.
7. **(Optional) Configure a custom domain** for the frontend and any required
   DNS / TLS.
8. **Rotate the GitHub PAT** used for pushes once deployment is complete — do
   not leave write-enabled tokens lying around.

---

## Swapping mock for real Huawei (future)

When real FusionSolar Northbound API credentials are obtained:

1. Set `HUAWEI_BASE_URL` to the real API URL.
2. Set `HUAWEI_USERNAME` / `HUAWEI_PASSWORD` to the real credentials.
3. Implement `HuaweiProvider.get_historical_readings` /
   `get_historical_weather` as real KPI-history polling loops (currently they
   return a single live snapshot, which is fine because Scarda reads history
   from its own DB).

No other part of the codebase changes — the provider abstraction isolates it.
