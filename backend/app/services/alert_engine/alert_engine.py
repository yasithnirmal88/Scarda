from __future__ import annotations

import logging
from datetime import datetime
from app.services.alert_engine.alert_generator import AlertGenerator
from app.services.alert_engine.alert_repository import BaseAlertRepository, InMemoryAlertRepository
from app.services.alert_engine.baseline_provider import (
    BaseBaselineProvider,
    StaticBaselineProvider,
    WeatherAwareBaselineProvider,
)
from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.confirmation_engine import (
    ConfirmationEngine,
    ConfirmationStatus,
)
from app.services.alert_engine.deviation_calculator import DeviationCalculator
from app.services.alert_engine.rule_engine import (
    CommunicationFailureRule,
    CurrentLowRule,
    OfflineRule,
    PowerLowRule,
    RuleRegistry,
    VoltageLowRule,
)
from app.services.alert_engine.types import AlertData, Reading
from app.utils.enums import AlertState

logger = logging.getLogger(__name__)


class AlertEngine:
    def __init__(
        self,
        config: AlertEngineConfig | None = None,
        baseline_provider: BaseBaselineProvider | None = None,
        repository: BaseAlertRepository | None = None,
    ) -> None:
        self._config = config or AlertEngineConfig()
        self._baseline_provider = baseline_provider or WeatherAwareBaselineProvider(self._config)
        self._repository = repository or InMemoryAlertRepository()
        self._deviation_calculator = DeviationCalculator()
        self._confirmation_engine = ConfirmationEngine(self._config)
        self._alert_generator = AlertGenerator(self._config)

        registry = RuleRegistry()
        registry.add_rule(OfflineRule(self._config))
        registry.add_rule(CommunicationFailureRule(self._config))
        registry.add_rule(CurrentLowRule(self._config))
        registry.add_rule(VoltageLowRule(self._config))
        registry.add_rule(PowerLowRule(self._config))
        self._rule_registry = registry

    def process_reading(self, reading: Reading) -> list[AlertData]:
        alerts: list[AlertData] = []

        weather = None
        if reading.irradiance is not None or reading.ambient_temperature is not None:
            weather = {
                "irradiance": reading.irradiance,
                "ambient_temperature": reading.ambient_temperature,
            }
        baseline = self._baseline_provider.get_baseline(reading.string_id, weather)
        deviation = self._deviation_calculator.calculate_deviation(reading, baseline)
        results = self._rule_registry.evaluate_all(reading, baseline, deviation)

        status = self._confirmation_engine.record_reading(
            reading.string_id, results, reading.timestamp
        )

        if status == ConfirmationStatus.CONFIRMED:
            result = results[0]
            alert = self._alert_generator.generate(result, deviation, reading.timestamp)
            existing = self._repository.find_active_by_string_and_type(
                reading.string_id, result.rule_name
            )
            if existing is not None:
                existing.timestamp = reading.timestamp
                logger.info("Duplicate prevented — updated timestamp for %s", existing.alert_id)
                alerts.append(existing)
            else:
                stored = self._repository.create(alert)
                alerts.append(stored)
                logger.info(
                    "Alert triggered: %s on %s — %s",
                    result.rule_name, reading.string_id, result.reason,
                )

        elif status == ConfirmationStatus.CLEARED:
            self._resolve_if_active(reading)

        return alerts

    def _resolve_if_active(self, reading: Reading) -> None:
        for rule_name in ("current_low", "voltage_low", "power_low", "offline", "communication_failure"):
            active = self._repository.find_active_by_string_and_type(reading.string_id, rule_name)
            if active is not None:
                resolved = self._repository.resolve(active.alert_id)
                if resolved is not None:
                    logger.info(
                        "Auto-resolved %s on %s — reading returned to normal",
                        resolved.alert_id, reading.string_id,
                    )

    def process_batch(self, readings: list[Reading]) -> list[AlertData]:
        all_alerts: list[AlertData] = []
        for reading in readings:
            alerts = self.process_reading(reading)
            all_alerts.extend(alerts)
        return all_alerts

    def get_active_alerts(self) -> list[AlertData]:
        return self._repository.get_active()

    @property
    def confirmation_pending_count(self) -> int:
        """Return the number of pending (unconfirmed) alert entries."""
        return self._confirmation_engine.pending_count

    def get_alert_history(self, limit: int = 100) -> list[AlertData]:
        return self._repository.get_history(limit)

    def acknowledge_alert(self, alert_id: str) -> AlertData | None:
        return self._repository.acknowledge(alert_id)

    def resolve_alert(self, alert_id: str) -> AlertData | None:
        return self._repository.resolve(alert_id)
