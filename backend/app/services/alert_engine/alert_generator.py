from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.recommandations import get_recommendation
from app.services.alert_engine.types import AlertData, AlertSeverity, AlertState, Deviation, RuleResult

logger = logging.getLogger(__name__)


def _parse_ids(string_id: str) -> tuple[str, str, str]:
    parts = string_id.split("-")
    if len(parts) >= 3:
        section = parts[0]
        inverter = f"{parts[0]}-{parts[1]}"
    elif len(parts) == 2:
        section = parts[0]
        inverter = string_id
    else:
        section = "unknown"
        inverter = "unknown"
    return section, inverter, string_id


class AlertGenerator:
    def __init__(self, config: AlertEngineConfig) -> None:
        self._config = config
        self._counter: int = 0

    def generate(
        self,
        rule_result: RuleResult,
        deviation: Deviation,
        timestamp: datetime,
    ) -> AlertData:
        self._counter += 1
        section, inverter, string = _parse_ids(rule_result.deviation.string_id)

        recommendation = ""
        if self._config.enable_recommendations:
            recommendation = get_recommendation(rule_result.rule_name)

        return AlertData(
            alert_id=f"ALERT-{timestamp.strftime('%Y%m%d-%H%M%S')}-{self._counter:04d}",
            timestamp=timestamp,
            section=section,
            inverter=inverter,
            string=string,
            alert_type=rule_result.rule_name,
            expected_value=rule_result.expected_value,
            actual_value=rule_result.actual_value,
            deviation_pct=rule_result.deviation_pct,
            severity=rule_result.severity,
            status=AlertState.ACTIVE,
            reason=rule_result.reason,
            recommendation=recommendation,
        )
