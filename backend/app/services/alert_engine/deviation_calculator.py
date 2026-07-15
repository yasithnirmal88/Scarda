from __future__ import annotations

import logging
from app.services.alert_engine.types import Baseline, Deviation, Reading

logger = logging.getLogger(__name__)


class DeviationCalculator:
    def calculate_percentage(self, actual: float, expected: float) -> float:
        if expected == 0:
            return 0.0
        return ((actual - expected) / expected) * 100.0

    def calculate_deviation(self, reading: Reading, baseline: Baseline) -> Deviation:
        deviation = Deviation(string_id=reading.string_id)

        if reading.current is not None:
            deviation.current_deviation = self._compute_absolute(
                reading.current, baseline.expected_current
            )
            deviation.current_deviation_pct = self.calculate_percentage(
                reading.current, baseline.expected_current
            )

        if reading.voltage is not None:
            deviation.voltage_deviation = self._compute_absolute(
                reading.voltage, baseline.expected_voltage
            )
            deviation.voltage_deviation_pct = self.calculate_percentage(
                reading.voltage, baseline.expected_voltage
            )

        if reading.power is not None:
            deviation.power_deviation = self._compute_absolute(
                reading.power, baseline.expected_power
            )
            deviation.power_deviation_pct = self.calculate_percentage(
                reading.power, baseline.expected_power
            )

        return deviation

    def _compute_absolute(self, actual: float, expected: float) -> float:
        return actual - expected
