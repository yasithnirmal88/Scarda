from __future__ import annotations

import httpx
import pytest

from app.config.huawei import HuaweiConfig
from app.providers.huawei.huawei_provider import (
    HuaweiProvider,
    huawei_to_scarda_string_id,
)

PLANT_SNAPSHOT = {
    "plant_id": "sim-plant-001",
    "timestamp": "2026-08-14T12:00:00Z",
    "power_kw": 245.5,
    "energy_today_kwh": 1850.0,
    "status": "ok",
    "metrics": {
        "irradiance_w_m2": 850.0,
        "ambient_temp_c": 28.5,
        "panel_temp_c": 38.0,
    },
    "inverters": [
        {"inverter_id": "inv-01", "power_w": 120000.0, "status": "ok"},
        {"inverter_id": "inv-02", "power_w": 125500.0, "status": "ok"},
    ],
    "strings": [
        {
            "string_id": "inv-01-str-001",
            "inverter_id": "inv-01",
            "current_a": 9.4,
            "voltage_v": 820.0,
            "power_w": 7708.0,
            "status": "ok",
            "timestamp": "2026-08-14T12:00:00Z",
        },
        {
            "string_id": "inv-02-str-003",
            "inverter_id": "inv-02",
            "current_a": 0.0,
            "voltage_v": 0.0,
            "power_w": 0.0,
            "status": "disconnected",
            "timestamp": "2026-08-14T12:00:00Z",
        },
    ],
}

TOKEN = "test-bearer-token"


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/api/auth/login" and request.method == "POST":
        return httpx.Response(200, json={"access_token": TOKEN, "token_type": "bearer"})
    if request.url.path == "/api/plants/sim-plant-001" and request.method == "GET":
        if request.headers.get("Authorization") != f"Bearer {TOKEN}":
            return httpx.Response(401, json={"detail": "Invalid token"})
        return httpx.Response(200, json=PLANT_SNAPSHOT)
    return httpx.Response(404, json={"detail": "Not found"})


def make_provider() -> tuple[HuaweiProvider, httpx.AsyncClient]:
    transport = httpx.MockTransport(_handler)
    client = httpx.AsyncClient(base_url="http://mock:8000", transport=transport)
    config = HuaweiConfig(
        BASE_URL="http://mock:8000",
        USERNAME="huawei",
        PASSWORD="huawei",
        PLANT_ID="sim-plant-001",
    )
    provider = HuaweiProvider(config=config, client=client)
    return provider, client


@pytest.mark.asyncio
async def test_login_and_health_check() -> None:
    provider, client = make_provider()
    try:
        result = await provider.health_check()
        assert result["status"] == "healthy"
        assert result["connected"] is True
        assert result["total_strings"] == 2
        assert result["total_inverters"] == 2
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_get_current_readings_maps_ids_and_values() -> None:
    provider, client = make_provider()
    try:
        data = await provider.get_current_readings()
        assert data["total_power_kw"] == 245.5
        assert data["daily_energy_kwh"] == 1850.0
        assert data["total_inverters"] == 2
        assert data["active_inverters"] == 2

        readings = data["readings"]
        assert len(readings) == 2
        assert readings[0]["string_id"] == "SEC01-INV01-STR01"
        assert readings[0]["current_a"] == 9.4
        assert readings[0]["voltage_v"] == 820.0
        assert readings[0]["power_w"] == 7708.0
        assert readings[1]["string_id"] == "SEC01-INV02-STR03"
        assert readings[1]["status"] == "disconnected"
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_get_weather_maps_metrics() -> None:
    provider, client = make_provider()
    try:
        weather = await provider.get_weather()
        assert weather["temperature_c"] == 28.5
        assert weather["irradiance_wpm2"] == 850.0
        assert weather["humidity_pct"] == 0.0
        assert weather["wind_speed_mps"] == 0.0
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_historical_readings_return_snapshot() -> None:
    provider, client = make_provider()
    try:
        from datetime import datetime, timezone

        start = datetime(2026, 8, 14, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 8, 14, 23, 59, tzinfo=timezone.utc)
        history = await provider.get_historical_readings(start, end)
        assert len(history) == 2
        assert all("timestamp" in r for r in history)

        weather_history = await provider.get_historical_weather(start, end)
        assert len(weather_history) == 1
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_token_refresh_on_401() -> None:
    """After a failed token, the provider re-authenticates and retries."""
    calls = {"login": 0, "plant": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/auth/login" and request.method == "POST":
            calls["login"] += 1
            return httpx.Response(200, json={"access_token": TOKEN, "token_type": "bearer"})
        if request.url.path.startswith("/api/plants/") and request.method == "GET":
            calls["plant"] += 1
            # First call uses a stale token, second (after re-auth) succeeds
            if calls["plant"] == 1 and request.headers.get("Authorization") != f"Bearer {TOKEN}":
                return httpx.Response(401, json={"detail": "Invalid token"})
            if calls["plant"] == 1 and request.headers.get("Authorization") == f"Bearer {TOKEN}":
                return httpx.Response(200, json=PLANT_SNAPSHOT)
            return httpx.Response(200, json=PLANT_SNAPSHOT)
        return httpx.Response(404, json={"detail": "Not found"})

    # Force an initial stale token so the 401-retry path is exercised
    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(base_url="http://mock:8000", transport=transport)
    config = HuaweiConfig(
        BASE_URL="http://mock:8000",
        USERNAME="huawei",
        PASSWORD="huawei",
        PLANT_ID="sim-plant-001",
    )
    provider = HuaweiProvider(config=config, client=client)
    provider._token = "stale-token"
    try:
        data = await provider.get_current_readings()
        assert data["total_power_kw"] == 245.5
    finally:
        await client.aclose()


def test_id_mapping_helpers() -> None:
    assert huawei_to_scarda_string_id("inv-01-str-001") == "SEC01-INV01-STR01"
    assert huawei_to_scarda_string_id("inv-12-str-020") == "SEC01-INV12-STR20"
    assert huawei_to_scarda_string_id("already-sec01") == "already-sec01"