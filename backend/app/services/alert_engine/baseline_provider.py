from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.types import Baseline


class BaseBaselineProvider(ABC):
    @abstractmethod
    def get_baseline(self, string_id: str) -> Baseline:
        ...

    @abstractmethod
    def get_baselines(self, string_ids: list[str]) -> dict[str, Baseline]:
        ...


class StaticBaselineProvider(BaseBaselineProvider):
    def __init__(self, config: AlertEngineConfig | None = None) -> None:
        self._config = config or AlertEngineConfig()

    def get_baseline(self, string_id: str) -> Baseline:
        return Baseline(
            string_id=string_id,
            expected_current=self._config.baseline_current,
            expected_voltage=self._config.baseline_voltage,
            expected_power=self._config.baseline_power,
        )

    def get_baselines(self, string_ids: list[str]) -> dict[str, Baseline]:
        return {sid: self.get_baseline(sid) for sid in string_ids}
