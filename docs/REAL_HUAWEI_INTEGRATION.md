# Real Huawei FusionSolar Integration — Readiness Checklist

This document records exactly what the current `HuaweiProvider` expects from the
upstream API and what information is still required from the company/Huawei to
switch from the Mock FusionSolar simulator to the real Northbound API.

> **All items below marked `REQUIRES COMPANY/HUAWEI VALIDATION` must be
> confirmed against the official Huawei FusionSolar Northbound API documentation
> before production deployment. The Mock FusionSolar implementation satisfies
> the same provider contract for development and testing.**

---

## 1. Authentication

| Item | Current (Mock) | Real Huawei | Status |
|------|---------------|-------------|--------|
| Login endpoint | `POST /api/auth/login` | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Credentials | username + password (JSON body) | **REQUIRES COMPANY/HUAWEI VALIDATION** — may use XSRF token, system ID, or OAuth | Unknown |
| Token field | `access_token` in JSON response | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Token type | Bearer token in `Authorization` header | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Token lifetime | None (re-auth on 401) | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |

The provider currently calls `POST {BASE_URL}{LOGIN_PATH}` with
`{"username": "...", "password": "..."}` and reads `access_token` from the
response. The real Huawei Northbound API uses a different auth scheme
(XSRF-TOKEN cookie + system ID). The `_login()` method will need adjustment.

---

## 2. API Base URL & Endpoints

| Item | Current (Mock) | Real Huawei | Status |
|------|---------------|-------------|--------|
| Base URL | `http://127.0.0.1:8001` | **REQUIRES COMPANY/HUAWEI VALIDATION** (e.g. `https://eu5.fusionsolar.huawei.com`) | Unknown |
| Plants path | `/api/plants` | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Plant snapshot | `GET /api/plants/{plant_id}` | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Readings history | `GET /api/plants/{plant_id}/history?start=...&end=...` | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Weather history | `GET /api/plants/{plant_id}/weather/history?start=...&end=...` | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |

---

## 3. Plant / Site Identifier

| Item | Current (Mock) | Real Huawei | Status |
|------|---------------|-------------|--------|
| Plant ID | `sim-plant-001` | **REQUIRES COMPANY/HUAWEI VALIDATION** — real plant code from FusionSolar | Unknown |
| ID format | String | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |

---

## 4. Current Readings Endpoint Contract

The provider's `get_current_readings()` expects a plant snapshot JSON:

```json
{
  "power_kw": 12.5,
  "energy_today_kwh": 45.2,
  "timestamp": "2026-08-15T12:00:00Z",
  "inverters": [{"status": "ok"}],
  "strings": [
    {
      "string_id": "SEC01-INV01-STR01",
      "current_a": 0.35,
      "voltage_v": 600.0,
      "power_w": 210.0,
      "status": "ok",
      "timestamp": "2026-08-15T12:00:00Z"
    }
  ],
  "metrics": {
    "irradiance_w_m2": 850.0,
    "ambient_temp_c": 26.0
  }
}
```

**REQUIRES COMPANY/HUAWEI VALIDATION:**
- Does the real API expose per-string current/voltage/power in a single plant snapshot?
- What are the actual JSON field names? (`current_a` vs `dcCurrent`, etc.)
- Is the timestamp ISO-8601 UTC or local time?
- What units are used? (A, V, W, kW)

---

## 5. Historical Readings Endpoint Contract

The provider's `get_historical_readings(start, end)` calls:
`GET /api/plants/{plant_id}/history?start=ISO&end=ISO`

Expects response:
```json
{
  "data": [
    {
      "string_id": "SEC01-INV01-STR01",
      "inverter_id": "SEC01-INV01",
      "current_a": 0.35,
      "voltage_v": 600.0,
      "power_w": 210.0,
      "status": "ok",
      "irradiance_w_m2": 850.0,
      "ambient_temp_c": 26.0,
      "timestamp": "2026-08-15T12:00:00Z"
    }
  ]
}
```

**REQUIRES COMPANY/HUAWEI VALIDATION:**
- What is the real historical data endpoint path?
- Does the real API return per-string historical data, or only plant-level KPIs?
- What is the maximum query range per request?
- Is pagination required? If so, what is the page size / cursor mechanism?
- What is the finest available resolution? (5-min, 10-min, 15-min, hourly, daily?)
- How far back is historical data available? (90 days, 1 year, indefinite?)

---

## 6. Weather Endpoint Contract

The provider's `get_weather()` and `get_historical_weather()` expect:

```json
{
  "ambient_temp_c": 26.0,
  "irradiance_w_m2": 850.0,
  "timestamp": "2026-08-15T12:00:00Z"
}
```

Currently, `humidity_pct`, `wind_speed_mps`, `wind_direction`, and
`precipitation_mm` are set to 0.0/"N/A" because the mock does not provide them.

**REQUIRES COMPANY/HUAWEI VALIDATION:**
- Does the real FusionSolar API expose ambient temperature and irradiance?
- Are these plant-level metrics or per-device?
- What other weather fields are available?
- Does Huawei provide weather history, or must Scarda integrate a third-party weather API?

---

## 7. Expected IDs

| Item | Current (Mock) | Real Huawei | Status |
|------|---------------|-------------|--------|
| String ID format | `SEC01-INV01-STR01` (composite) | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Inverter ID format | `SEC01-INV01` | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| ID mapping | `huawei_to_scarda_string_id()` | **REQUIRES COMPANY/HUAWEI VALIDATION** — mapping logic may need to change | Unknown |

---

## 8. Timestamp Format

| Item | Current (Mock) | Real Huawei | Status |
|------|---------------|-------------|--------|
| Format | ISO-8601 with timezone (`2026-08-15T12:00:00Z`) | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Timezone | UTC | **REQUIRES COMPANY/HUAWEI VALIDATION** — may be local time | Unknown |
| Preserved in DB | ✅ `recorded_at` stores original measurement time | Must be verified after integration | Pending |

---

## 9. Units

| Metric | Current (Mock) | Real Huawei | Status |
|--------|---------------|-------------|--------|
| Current | Amperes (A) | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Voltage | Volts (V) | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Power | Watts (W) | **REQUIRES COMPANY/HUAWEI VALIDATION** — may be kW | Unknown |
| Irradiance | W/m² | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Temperature | °C | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |

---

## 10. Polling Frequency

| Item | Current | Real Huawei | Status |
|------|---------|-------------|--------|
| Live polling interval | 10 minutes (configurable via `SCHEDULER_SIMULATOR_INTERVAL_MINUTES`) | **REQUIRES COMPANY/HUAWEI VALIDATION** — API rate limits unknown | Unknown |
| Rate limit | None (mock) | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |

---

## 11. Historical Data Availability

| Item | Current (Mock) | Real Huawei | Status |
|------|---------------|-------------|--------|
| Lookback | 90 days | **REQUIRES COMPANY/HUAWEI VALIDATION** | Unknown |
| Resolution | 10-minute intervals | **REQUIRES COMPANY/HUAWEI VALIDATION** — may be 5-min, 15-min, hourly, or daily | Unknown |
| Backfill batch size | Single request for full range | **REQUIRES COMPANY/HUAWEI VALIDATION** — may need chunking | Unknown |

---

## 12. Pagination / Batching

**REQUIRES COMPANY/HUAWEI VALIDATION:**
- Does the real API support arbitrary date ranges in a single request?
- Is there a maximum number of records per response?
- Is cursor-based or page-based pagination used?
- The current provider does NOT paginate — it assumes all data fits in one response.

---

## 13. Unknown Fields

The following fields in the provider contract may not exist in the real Huawei API and would need fallback behavior:

- `humidity_pct` — currently hardcoded to 0.0
- `wind_speed_mps` — currently hardcoded to 0.0
- `wind_direction` — currently hardcoded to "N/A"
- `precipitation_mm` — currently hardcoded to 0.0
- `energy_today_kwh` — used in current readings response
- `active_inverters` / `total_inverters` — derived from inverter list

**REQUIRES COMPANY/HUAWEI VALIDATION:** Which of these fields are available in the real API?

---

## Summary

The `HuaweiProvider` implements the full `IDataProvider` contract (current
readings, historical readings, current weather, historical weather) and works
end-to-end against the Mock FusionSolar simulator. To switch to the real Huawei
FusionSolar Northbound API, the following must be provided by the company:

1. **API base URL** and authentication scheme
2. **Plant/site code** identifier
3. **API documentation** confirming endpoint paths, field names, and response formats
4. **Rate limits** and polling frequency guidance
5. **Historical data availability** (lookback period, resolution, pagination)
6. **Weather data availability** (which fields Huawei provides)

Until these are validated, the system is **NOT production-ready** for real Huawei
integration. All algorithmic validation (anomaly detection, historical
similarity, confirmation engine, alerts) has been verified against the Mock
FusionSolar simulator and real TimescaleDB.
