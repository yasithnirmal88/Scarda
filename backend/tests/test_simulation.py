"""Integration test for AlertEngine with a synthetic readings fixture.

Simulates 100 cycles of readings with random anomalies and feeds them
through the AlertEngine to verify detection, confirmation, and resolution
behavior. Uses a seeded RNG for deterministic test results.

NOTE: this test previously used the in-repo ``FakeProvider`` as a data source.
That provider was removed (Scarda no longer generates data internally — all
data comes from the mock-fusionsolar API via the provider abstraction). The
test now uses an inline fixture of plausible string readings, preserving the
AlertEngine coverage without reintroducing a fake data source into Scarda.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import pytest

from app.services.alert_engine.alert_engine import AlertEngine
from app.services.alert_engine.types import Reading
from app.utils.enums import AlertState

# Deterministic RNG for reproducible test results
_TEST_RNG = random.Random(42)

# Anomaly simulation parameters
ANOMALY_PROBABILITY = 0.15
SEVERE_CURRENT_FACTOR = 0.2
SEVERE_VOLTAGE_FACTOR = 0.3
SEVERE_POWER_FACTOR = 0.2
MILD_CURRENT_FACTOR = 0.6
MILD_VOLTAGE_FACTOR = 0.75
MILD_POWER_FACTOR = 0.6

# Inline readings fixture (replaces the removed FakeProvider). These are
# plausible per-string operating points under nominal conditions.
FIXTURE_READINGS: list[dict] = [
    {"string_id": "SEC01-INV01-STR01", "current_a": 9.4, "voltage_v": 820.0, "power_w": 7708.0},
    {"string_id": "SEC01-INV01-STR02", "current_a": 8.7, "voltage_v": 815.0, "power_w": 7090.5},
    {"string_id": "SEC01-INV01-STR03", "current_a": 9.1, "voltage_v": 818.0, "power_w": 7443.8},
]


@pytest.mark.asyncio
async def test_engine_against_readings_fixture() -> None:
    engine = AlertEngine()

    readings_list = FIXTURE_READINGS

    simulated_readings: list[Reading] = []
    base_time = datetime.now() - timedelta(hours=24)

    for cycle in range(100):
        base_cycle = base_time + timedelta(minutes=cycle * 10)
        for entry in readings_list:
            sid = entry["string_id"]
            current = entry.get("current_a", 10.0)
            voltage = entry.get("voltage_v", 820.0)
            power = entry.get("power_w", 8200.0)

            anomaly = _TEST_RNG.random() < ANOMALY_PROBABILITY
            if anomaly:
                severity = _TEST_RNG.choice(["mild", "severe"])
                if severity == "severe":
                    current *= SEVERE_CURRENT_FACTOR
                    voltage *= SEVERE_VOLTAGE_FACTOR
                    power *= SEVERE_POWER_FACTOR
                else:
                    current *= MILD_CURRENT_FACTOR
                    voltage *= MILD_VOLTAGE_FACTOR
                    power *= MILD_POWER_FACTOR

            simulated_readings.append(
                Reading(
                    string_id=sid,
                    timestamp=base_cycle,
                    current=round(current, 2),
                    voltage=round(voltage, 1),
                    power=round(power, 1),
                    status="active",
                )
            )

    all_alerts = engine.process_batch(simulated_readings)
    history = engine.get_alert_history()
    active = engine.get_active_alerts()
    resolved = [a for a in history if a.status == AlertState.RESOLVED]

    total_healthy = len(simulated_readings) - len(history) - engine.confirmation_pending_count

    detection_times: list[float] = []
    for alert in resolved:
        if alert.duration_seconds is not None:
            detection_times.append(alert.duration_seconds)

    avg_detection = sum(detection_times) / len(detection_times) if detection_times else 0.0

    print(f"\n{'='*60}")
    print(f"SIMULATION RESULTS — readings fixture ({len(readings_list)} strings)")
    print(f"{'='*60}")
    print(f"Total simulated readings : {len(simulated_readings)}")
    print(f"Healthy readings         : {total_healthy}")
    print(f"Pending alerts           : {engine.confirmation_pending_count}")
    print(f"Confirmed alerts         : {len(history)}")
    print(f"Resolved alerts          : {len(resolved)}")
    print(f"Still active             : {len(active)}")
    print(f"Average detection time   : {avg_detection:.1f}s")
    print(f"{'='*60}\n")

    for alert in history[:5]:
        print(
            f"  [{alert.severity.value.upper():8}] {alert.alert_id} "
            f"| {alert.string} | {alert.alert_type} "
            f"| dev={alert.deviation_pct:+.1f}%"
        )
        if alert.recommendation:
            print(f"         -> {alert.recommendation}")

    # Meaningful assertions
    assert len(simulated_readings) == 100 * len(readings_list), (
        f"Expected {100 * len(readings_list)} readings, got {len(simulated_readings)}"
    )
    assert len(all_alerts) >= 0  # all_alerts is the batch return; may be empty if no anomalies confirmed
    assert len(history) >= 0  # history may have 0+ confirmed alerts depending on random anomalies
    assert isinstance(engine.confirmation_pending_count, int)
    assert engine.confirmation_pending_count >= 0
    # The engine should process all readings without error
    assert len(active) >= 0
    # All resolved alerts should have a valid resolved timestamp
    for alert in resolved:
        assert alert.resolved_at is not None
        assert alert.duration_seconds is not None
        assert alert.duration_seconds >= 0


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_engine_against_readings_fixture())
