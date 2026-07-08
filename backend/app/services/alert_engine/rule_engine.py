from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.types import AlertSeverity, Baseline, Deviation, Reading, RuleResult

logger = logging.getLogger(__name__)


class BaseRule(ABC):
    def __init__(self, config: AlertEngineConfig) -> None:
        self._config = config

    @abstractmethod
    def evaluate(self, reading: Reading, baseline: Baseline, deviation: Deviation) -> RuleResult | None:
        ...

    def _map_severity(self, deviation_pct: float) -> AlertSeverity:
        abs_dev = abs(deviation_pct)
        if abs_dev >= self._config.severity_critical_threshold:
            return AlertSeverity.CRITICAL
        if abs_dev >= self._config.severity_warning_threshold:
            return AlertSeverity.WARNING
        return AlertSeverity.INFO


class CurrentLowRule(BaseRule):
    def evaluate(self, reading: Reading, baseline: Baseline, deviation: Deviation) -> RuleResult | None:
        if reading.current is None:
            return None
        pct = deviation.current_deviation_pct
        if pct is None:
            return None
        if pct < -self._config.current_threshold_pct and reading.current <= self._config.offline_current_threshold:
            return RuleResult(
                triggered=True,
                rule_name="current_low",
                reason=f"Current {reading.current:.2f}A is {abs(pct):.1f}% below expected {baseline.expected_current:.1f}A",
                severity=self._map_severity(pct),
                deviation=deviation,
                expected_value=baseline.expected_current,
                actual_value=reading.current,
                deviation_pct=pct,
            )
        if pct < -self._config.current_threshold_pct:
            return RuleResult(
                triggered=True,
                rule_name="current_low",
                reason=f"Current {reading.current:.2f}A is {abs(pct):.1f}% below expected {baseline.expected_current:.1f}A",
                severity=self._map_severity(pct),
                deviation=deviation,
                expected_value=baseline.expected_current,
                actual_value=reading.current,
                deviation_pct=pct,
            )
        return None


class VoltageLowRule(BaseRule):
    def evaluate(self, reading: Reading, baseline: Baseline, deviation: Deviation) -> RuleResult | None:
        if reading.voltage is None:
            return None
        pct = deviation.voltage_deviation_pct
        if pct is None:
            return None
        if pct < -self._config.voltage_threshold_pct:
            return RuleResult(
                triggered=True,
                rule_name="voltage_low",
                reason=f"Voltage {reading.voltage:.1f}V is {abs(pct):.1f}% below expected {baseline.expected_voltage:.1f}V",
                severity=self._map_severity(pct),
                deviation=deviation,
                expected_value=baseline.expected_voltage,
                actual_value=reading.voltage,
                deviation_pct=pct,
            )
        return None


class PowerLowRule(BaseRule):
    def evaluate(self, reading: Reading, baseline: Baseline, deviation: Deviation) -> RuleResult | None:
        if reading.power is None:
            return None
        pct = deviation.power_deviation_pct
        if pct is None:
            return None
        if pct < -self._config.power_threshold_pct:
            return RuleResult(
                triggered=True,
                rule_name="power_low",
                reason=f"Power {reading.power:.1f}W is {abs(pct):.1f}% below expected {baseline.expected_power:.1f}W",
                severity=self._map_severity(pct),
                deviation=deviation,
                expected_value=baseline.expected_power,
                actual_value=reading.power,
                deviation_pct=pct,
            )
        return None


class OfflineRule(BaseRule):
    def evaluate(self, reading: Reading, baseline: Baseline, deviation: Deviation) -> RuleResult | None:
        if reading.current is None or reading.voltage is None:
            return None
        current_ok = reading.current <= self._config.offline_current_threshold
        voltage_ok = reading.voltage <= self._config.offline_voltage_threshold
        if current_ok and voltage_ok:
            return RuleResult(
                triggered=True,
                rule_name="offline",
                reason=f"String offline — current {reading.current:.2f}A, voltage {reading.voltage:.1f}V",
                severity=AlertSeverity.CRITICAL,
                deviation=deviation,
                actual_value=reading.current,
            )
        return None


class CommunicationFailureRule(BaseRule):
    def evaluate(self, reading: Reading, baseline: Baseline, deviation: Deviation) -> RuleResult | None:
        if reading.status == "offline":
            return RuleResult(
                triggered=True,
                rule_name="communication_failure",
                reason=f"String {reading.string_id} status is offline",
                severity=AlertSeverity.CRITICAL,
                deviation=deviation,
            )
        return None


class RuleRegistry:
    def __init__(self, rules: list[BaseRule] | None = None) -> None:
        self._rules: list[BaseRule] = rules or []

    def add_rule(self, rule: BaseRule) -> None:
        self._rules.append(rule)

    def evaluate_all(self, reading: Reading, baseline: Baseline, deviation: Deviation) -> list[RuleResult]:
        results: list[RuleResult] = []
        for rule in self._rules:
            try:
                result = rule.evaluate(reading, baseline, deviation)
                if result is not None and result.triggered:
                    logger.info("Rule triggered: %s for %s", result.rule_name, reading.string_id)
                    results.append(result)
            except Exception:
                logger.exception("Rule evaluation failed for %s", rule.__class__.__name__)
        return results
