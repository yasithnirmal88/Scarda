from datetime import datetime
from typing import Any

from app.providers.base_provider import IDataProvider
from simulator.models import SimulatorConfig
from simulator.simulation_controller import SimulationController


class SimulatorDataProvider(IDataProvider):
    """Wraps SimulationController to conform to IDataProvider.

    This provider acts as the live data source until the real Huawei
    Smart Logger integration is implemented.
    """

    def __init__(self, config: SimulatorConfig | None = None) -> None:
        self._sim = SimulationController(config=config)

    async def get_current_readings(self) -> dict[str, Any]:
        return await self._sim.get_current_readings()

    async def get_weather(self) -> dict[str, Any]:
        return await self._sim.get_weather()

    async def get_historical_readings(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        return await self._sim.get_historical_readings(start, end)

    async def get_historical_weather(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        return await self._sim.get_historical_weather(start, end)

    async def health_check(self) -> dict[str, Any]:
        return await self._sim.health_check()
