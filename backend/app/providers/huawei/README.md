# Huawei Data Provider

Implementation of the `IDataProvider` contract backed by the Huawei
FusionSolar Northbound API.

## Status

Implemented. In the current development environment the provider talks to the
local `mock-fusionsolar-api` simulator (already cloned), which exposes the same
`POST /api/auth/login` + `GET /api/plants/{plant_id}` surface as the real
Northbound API. The rest of the application needs no changes — it only depends
on the `IDataProvider` interface.

## Configuration

Enabled via `PROVIDER_TYPE=huawei`. All settings use the `HUAWEI_` prefix:

| Variable | Default | Description |
|---|---|---|
| `HUAWEI_BASE_URL` | `http://127.0.0.1:8000` | Base URL of the API (mock or real) |
| `HUAWEI_USERNAME` | `huawei` | API login username |
| `HUAWEI_PASSWORD` | `huawei` | API login password |
| `HUAWEI_PLANT_ID` | `sim-plant-001` | Plant to monitor |
| `HUAWEI_TIMEOUT_SECONDS` | `10.0` | HTTP request timeout |
| `HUAWEI_LOGIN_PATH` | `/api/auth/login` | Auth endpoint path |
| `HUAWEI_PLANTS_PATH` | `/api/plants` | Plants endpoint path |

## Data mapping

The mock exposes plant data under raw ids like `inv-01-str-001`. The provider
remaps them to Scarda's convention (`SEC01-INV01-STR01`) so the frontend
hierarchy, alert engine and dashboards work unchanged.

Weather fields not provided by the mock (humidity, wind, precipitation) are
returned as neutral defaults.

## Limitations

- The mock has no native history endpoint, so `get_historical_readings` /
  `get_historical_weather` return a single live snapshot. When moving to the
  real API, replace these with KPI-history polling.