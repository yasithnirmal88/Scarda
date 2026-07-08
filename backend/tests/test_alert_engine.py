from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.services.alert_engine.alert_engine import AlertEngine
from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.types import AlertState, Reading


def _reading(
    string_id: str,
    current: float | None = 10.0,
    voltage: float | None = 820.0,
    power: float | None = 8200.0,
    status: str = "active",
    offset_minutes: int = 0,
) -> Reading:
    return Reading(
        string_id=string_id,
        timestamp=datetime.now() - timedelta(minutes=offset_minutes),
        current=current,
        voltage=voltage,
        power=power,
        status=status,
    )


class TestHealthyReading:
    def test_no_alerts_for_normal_readings(self) -> None:
        engine = AlertEngine()
        reading = _reading("SEC01-INV01-STR01")
        alerts = engine.process_reading(reading)
        assert len(alerts) == 0
        assert len(engine.get_active_alerts()) == 0

    def test_multiple_normal_readings_no_alerts(self) -> None:
        engine = AlertEngine()
        for i in range(5):
            alerts = engine.process_reading(
                _reading(f"SEC01-INV01-STR{i:02d}")
            )
            assert len(alerts) == 0
        assert len(engine.get_active_alerts()) == 0


class TestSingleBadReading:
    def test_one_bad_reading_creates_pending_only(self) -> None:
        engine = AlertEngine()
        reading = _reading("SEC01-INV01-STR01", current=3.0)
        alerts = engine.process_reading(reading)
        assert len(alerts) == 0
        assert len(engine.get_active_alerts()) == 0

    def test_if_reading_recovers_no_alert(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", current=3.0))
        alerts = engine.process_reading(_reading("SEC01-INV01-STR01", current=10.0))
        assert len(alerts) == 0
        assert len(engine.get_active_alerts()) == 0


class TestTwoConsecutiveBadReadings:
    def test_two_bad_readings_triggers_alert(self) -> None:
        engine = AlertEngine()
        r1 = _reading("SEC01-INV01-STR01", current=3.0)
        r2 = _reading("SEC01-INV01-STR01", current=2.8, offset_minutes=10)

        a1 = engine.process_reading(r1)
        a2 = engine.process_reading(r2)

        assert len(a1) == 0
        assert len(a2) >= 1
        active = engine.get_active_alerts()
        assert len(active) >= 1
        assert active[0].alert_type == "current_low"
        assert active[0].severity.value == "critical"

    def test_three_consecutive_bad_readings_one_alert(self) -> None:
        engine = AlertEngine()
        for i in range(3):
            alerts = engine.process_reading(
                _reading("SEC01-INV01-STR01", current=2.5, offset_minutes=i * 10)
            )
        active = engine.get_active_alerts()
        assert len(active) == 1


class TestRecoveredReading:
    def test_alert_resolves_when_reading_recovers(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", current=3.0))
        engine.process_reading(_reading("SEC01-INV01-STR01", current=2.8, offset_minutes=10))
        active = engine.get_active_alerts()
        assert len(active) == 1
        current_low = active[0]

        for i in range(3):
            engine.process_reading(
                _reading("SEC01-INV01-STR01", current=10.0, offset_minutes=20 + i * 10)
            )

        history = engine.get_alert_history()
        resolved = [a for a in history if a.alert_id == current_low.alert_id]
        assert len(resolved) == 1
        assert resolved[0].status == AlertState.RESOLVED

    def test_pending_cleared_on_recovery(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", current=3.0))
        alerts = engine.process_reading(_reading("SEC01-INV01-STR01", current=10.0, offset_minutes=10))
        assert len(alerts) == 0
        assert len(engine.get_active_alerts()) == 0


class TestDuplicateAlertPrevention:
    def test_no_duplicate_alerts_for_same_string_type(self) -> None:
        engine = AlertEngine()
        for i in range(4):
            engine.process_reading(
                _reading("SEC01-INV01-STR01", current=3.0, offset_minutes=i * 10)
            )
        active = engine.get_active_alerts()
        current_alerts = [a for a in active if a.alert_type == "current_low"]
        assert len(current_alerts) == 1

    def test_different_strings_separate_alerts(self) -> None:
        engine = AlertEngine()
        for sid in ("SEC01-INV01-STR01", "SEC01-INV01-STR02"):
            for i in range(2):
                engine.process_reading(
                    _reading(sid, current=3.0, offset_minutes=i * 10)
                )
        assert len(engine.get_active_alerts()) == 2


class TestOfflineString:
    def test_offline_detected(self) -> None:
        engine = AlertEngine()
        reading = _reading("SEC01-INV01-STR01", current=0.0, voltage=0.0)
        alerts = engine.process_reading(reading)
        assert len(alerts) == 0

        reading2 = _reading("SEC01-INV01-STR01", current=0.0, voltage=0.0, offset_minutes=10)
        alerts = engine.process_reading(reading2)
        assert len(alerts) >= 1
        active = engine.get_active_alerts()
        offline_alerts = [a for a in active if a.alert_type == "offline"]
        assert len(offline_alerts) == 1


class TestVoltageFailure:
    def test_voltage_low_alert(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", voltage=400.0))
        alerts = engine.process_reading(
            _reading("SEC01-INV01-STR01", voltage=380.0, offset_minutes=10)
        )
        assert len(alerts) >= 1
        active = engine.get_active_alerts()
        voltage_alerts = [a for a in active if a.alert_type == "voltage_low"]
        assert len(voltage_alerts) == 1


class TestCurrentFailure:
    def test_current_low_alert(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", current=2.0))
        alerts = engine.process_reading(
            _reading("SEC01-INV01-STR01", current=1.8, offset_minutes=10)
        )
        assert len(alerts) >= 1
        active = engine.get_active_alerts()
        current_alerts = [a for a in active if a.alert_type == "current_low"]
        assert len(current_alerts) == 1


class TestAcknowledgeResolve:
    def test_acknowledge_alert(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", current=3.0))
        engine.process_reading(_reading("SEC01-INV01-STR01", current=2.8, offset_minutes=10))
        active = engine.get_active_alerts()
        assert len(active) == 1
        result = engine.acknowledge_alert(active[0].alert_id)
        assert result is not None
        assert result.status == AlertState.ACKNOWLEDGED

    def test_resolve_alert(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", current=3.0))
        engine.process_reading(_reading("SEC01-INV01-STR01", current=2.8, offset_minutes=10))
        active = engine.get_active_alerts()
        result = engine.resolve_alert(active[0].alert_id)
        assert result is not None
        assert result.status == AlertState.RESOLVED
        assert result.resolved_at is not None
        assert result.duration_seconds is not None


class TestBatchProcessing:
    def test_process_batch_returns_all_alerts(self) -> None:
        engine = AlertEngine()
        readings = []
        for i in range(2):
            readings.append(
                _reading(f"SEC01-INV01-STR{i:02d}", current=3.0, offset_minutes=i * 10)
            )
        readings.append(
            _reading("SEC01-INV01-STR00", current=3.0, offset_minutes=20)
        )
        alerts = engine.process_batch(readings)
        assert len(alerts) >= 1


class TestAlertHistory:
    def test_history_includes_all_alerts(self) -> None:
        engine = AlertEngine()
        engine.process_reading(_reading("SEC01-INV01-STR01", current=3.0))
        engine.process_reading(_reading("SEC01-INV01-STR01", current=2.8, offset_minutes=10))
        engine.process_reading(_reading("SEC02-INV01-STR01", current=3.0))
        engine.process_reading(_reading("SEC02-INV01-STR01", current=2.8, offset_minutes=10))
        history = engine.get_alert_history()
        assert len(history) == 2
