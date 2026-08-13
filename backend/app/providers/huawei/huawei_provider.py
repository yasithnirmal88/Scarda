from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config.huawei import HuaweiConfig
from app.providers.interfaces import IDataProvider

logger = logging.getLogger(__name__)


def huawei_to_scarda_string_id(raw: str) -> str:
    """Map a mock FusionSolar string id (e.g. ``inv-01-str-001``) to the Scarda
    convention (``SEC01-INV01-STR01``).

    The mock simulator exposes only two inverters, so all inverters are placed
    in the first section. Unknown / already-normalised ids are returned as-is.
    """
    parts = raw.split("-")
    if len(parts) == 4 and parts[0] == "inv" and parts[2] == "str":
        try:
            inv = int(parts[1])
            string = int(parts[3])
        except ValueError:
            return raw
        return f"SEC01-INV{inv:02d}-STR{string:02d}"
    return raw


def huawei_to_scarda_inverter_id(raw: str) -> str:
    parts = raw.split("-")
    if len(parts) == 2 and parts[0] == "inv":
        try:
            inv = int(parts[1])
        except ValueError:
            return raw
        return f"SEC01-INV{inv:02d}"
    return raw


class HuaweiProvider(IDataProvider):
    """Data provider for the Huawei FusionSolar Northbound API.

    Implements the full ``IDataProvider`` contract. In the current development
    environment it talks to the local ``mock-fusionsolar-api`` simulator, which
    exposes the same auth/plant/string endpoints as the real Northbound API.

    Data returned by the mock is remapped to Scarda's string convention
    (``SEC01-INV01-STR01``) so dashboards, alerts and the plant hierarchy work
    unchanged.

    Note: the mock simulator has no native history endpoint, so the historical
    methods return the current live snapshot mapped into the requested window.
    Swap ``BASE_URL``/credentials to point at the real API later.
    """

    def __init__(
        self,
        config: HuaweiConfig | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._config = config or HuaweiConfig()
        if client is not None:
            self._client = client
        else:
            self._client = httpx.AsyncClient(
                base_url=self._config.BASE_URL,
                timeout=self._config.TIMEOUT_SECONDS,
            )
        self._token: str | None = None
        self._token_expires_at: datetime | None = None

    # -- auth -----------------------------------------------------------------

    async def _login(self) -> str:
        resp = await self._client.post(
            self._config.LOGIN_PATH,
            json={"username": self._config.USERNAME, "password": self._config.PASSWORD},
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data.get("access_token")
        logger.info("HuaweiProvider authenticated (login=%s)", self._config.USERNAME)
        return self._token or ""

    async def _auth_headers(self) -> dict[str, str]:
        if not self._token:
            await self._login()
        return {"Authorization": f"Bearer {self._token}"}

    # -- plant fetch ----------------------------------------------------------

    async def _get_plant_snapshot(self) -> dict[str, Any]:
        headers = await self._auth_headers()
        url = f"{self._config.PLANTS_PATH}/{self._config.PLANT_ID}"
        resp = await self._client.get(url, headers=headers)

        # Re-auth once if the token was rejected/expired server-side
        if resp.status_code == 401:
            self._token = None
            headers = await self._auth_headers()
            resp = await self._client.get(url, headers=headers)

        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _map_readings(plant: dict[str, Any]) -> list[dict[str, Any]]:
        readings: list[dict[str, Any]] = []
        for s in plant.get("strings", []):
            readings.append(
                {
                    "string_id": huawei_to_scarda_string_id(s.get("string_id", "")),
                    "current_a": s.get("current_a"),
                    "voltage_v": s.get("voltage_v"),
                    "power_w": s.get("power_w"),
                    "status": s.get("status"),
                    "timestamp": s.get("timestamp"),
                }
            )
        return readings

    @staticmethod
    def _map_weather(plant: dict[str, Any]) -> dict[str, Any]:
        metrics = plant.get("metrics", {})
        return {
            "temperature_c": metrics.get("ambient_temp_c"),
            "humidity_pct": 0.0,  # not provided by the mock FusionSolar API
            "irradiance_wpm2": metrics.get("irradiance_w_m2"),
            "wind_speed_mps": 0.0,  # not provided by the mock FusionSolar API
            "wind_direction": "N/A",  # not provided by the mock FusionSolar API
            "precipitation_mm": 0.0,  # not provided by the mock FusionSolar API
            "timestamp": plant.get("timestamp"),
        }

    # -- IDataProvider --------------------------------------------------------

    async def get_current_readings(self) -> dict[str, Any]:
        """Return current readings for all strings exposed by the plant."""
        plant = await self._get_plant_snapshot()
        readings = self._map_readings(plant)
        inverters = plant.get("inverters", [])
        total_inverters = len(inverters)
        active_inverters = sum(
            1 for inv in inverters if inv.get("status") in ("ok", "active", "online", "running")
        )
        return {
            "total_power_kw": plant.get("power_kw"),
            "daily_energy_kwh": plant.get("energy_today_kwh"),
            "active_inverters": active_inverters or total_inverters,
            "total_inverters": total_inverters,
            "readings": readings,
            "timestamp": plant.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        }

    async def get_weather(self) -> dict[str, Any]:
        plant = await self._get_plant_snapshot()
        return self._map_weather(plant)

    async def get_historical_readings(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        """Return readings within a time range.

        The mock FusionSolar simulator exposes no history endpoint, so a single
        live snapshot is returned. Each reading inherits the plant snapshot
        timestamp. Replace with a real KPI-history loop for the live API.
        """
        plant = await self._get_plant_snapshot()
        ts = plant.get("timestamp") or datetime.now(timezone.utc).isoformat()
        readings = self._map_readings(plant)
        for rd in readings:
            rd["timestamp"] = ts
        return readings

    async def get_historical_weather(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        plant = await self._get_plant_snapshot()
        return [self._map_weather(plant)]

    async def health_check(self) -> dict[str, Any]:
        try:
            plant = await self._get_plant_snapshot()
            n_strings = len(plant.get("strings", []))
            n_inverters = len(plant.get("inverters", []))
            return {
                "status": "healthy",
                "provider": "huawei",
                "connected": True,
                "plant_id": self._config.PLANT_ID,
                "total_strings": n_strings,
                "total_inverters": n_inverters,
            }
        except httpx.HTTPError as exc:
            return {
                "status": "degraded",
                "provider": "huawei",
                "connected": False,
                "message": str(exc),
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Huawei health check failed: %s", exc)
            return {
                "status": "unavailable",
                "provider": "huawei",
                "connected": False,
                "message": str(exc),
            }