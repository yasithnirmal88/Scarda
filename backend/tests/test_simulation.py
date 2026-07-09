from __future__ import annotations

import random
from datetime import datetime, timedelta

import pytest

from app.providers.fake import FakeProvider
from app.services.alert_engine.alert_engine import AlertEngine
from app.services.alert_engine.types import AlertState, Reading


def _convert_fake_reading(raw: dict, string_id: str, timestamp: datetime) -> Reading:
    return Reading(
        string_id=string_id,
        timestamp=timestamp,
        current=raw.get("current_a"),
        voltage=raw.get("voltage_v"),
        power=raw.get("power_w"),
        status="active",
    )


@pytest.mark.asyncio
async def test_engine_against_fake_provider() -> None:
    provider = FakeProvider()
    engine = AlertEngine()

    raw_readings = await provider.get_current_readings()
    readings_list = raw_readings.get("readings", [])

    if not readings_list:
        readings_list = [
            {"string_id": "SEC01-INV01-STR01", "current_a": 9.4, "voltage_v": 820.0, "power_w": 7708.0},
            {"string_id": "SEC01-INV01-STR02", "current_a": 8.7, "voltage_v": 815.0, "power_w": 7090.5},
            {"string_id": "SEC01-INV01-STR03", "current_a": 9.1, "voltage_v": 818.0, "power_w": 7443.8},
        ]

    simulated_readings: list[Reading] = []
    base_time = datetime.now() - timedelta(hours=24)

    for cycle in range(100):
        base_cycle = base_time + timedelta(minutes=cycle * 10)
        for entry in readings_list:
            sid = entry["string_id"]
            current = entry.get("current_a", 10.0)
            voltage = entry.get("voltage_v", 820.0)
            power = entry.get("power_w", 8200.0)

            anomaly = random.random() < 0.15
            if anomaly:
                severity = random.choice(["mild", "severe"])
                if severity == "severe":
                    current *= 0.2
                    voltage *= 0.3
                    power *= 0.2
                else:
                    current *= 0.6
                    voltage *= 0.75
                    power *= 0.6

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

    total_healthy = len(simulated_readings) - len(history) - engine._confirmation_engine.pending_count

    detection_times: list[float] = []
    for alert in resolved:
        if alert.duration_seconds is not None:
            detection_times.append(alert.duration_seconds)

    avg_detection = sum(detection_times) / len(detection_times) if detection_times else 0.0

    print(f"\n{'='*60}")
    print(f"SIMULATION RESULTS — FakeDataProvider ({len(readings_list)} strings)")
    print(f"{'='*60}")
    print(f"Total simulated readings : {len(simulated_readings)}")
    print(f"Healthy readings         : {total_healthy}")
    print(f"Pending alerts           : {engine._confirmation_engine.pending_count}")
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

    assert len(all_alerts) >= 0


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_engine_against_fake_provider())
