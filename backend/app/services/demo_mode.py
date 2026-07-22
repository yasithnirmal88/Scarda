from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from math import sin, pi

from app.events.event_bus import EventBus
from app.events.events import ReadingGenerated
from app.events.handlers import SchedulerTickHandler
from app.providers.interfaces import IDataProvider

logger = logging.getLogger(__name__)

HOURS = 24
INTERVAL_MINUTES = 10
STEPS = int(HOURS * 60 / INTERVAL_MINUTES)


def _daylight_factor(hour: float) -> float:
    """Return a 0-1 factor for solar generation based on hour of day.

    Uses a sine curve peaking at 12:30 (solar noon).
    """
    radians = (hour - 5.0) * pi / 14.0
    return max(0.0, min(1.0, sin(radians)))


async def run_demo_once(
    provider: IDataProvider,
    event_bus: EventBus,
) -> None:
    """Generate one full day of historical readings and feed them through
    the event bus pipeline (storage → alert engine → WebSocket)."""

    logger.info("Demo mode: generating %d historical reading batches...", STEPS)

    base_readings = await provider.get_current_readings()
    base_weather = await provider.get_weather()

    if isinstance(base_readings, dict):
        base_list = base_readings.get("readings", [])
    else:
        base_list = base_readings

    if not base_list:
        logger.warning("Demo mode: no base readings available, skipping")
        return

    now = datetime.now(timezone.utc)
    day_start = now - timedelta(hours=HOURS)

    for i in range(STEPS):
        timestamp = day_start + timedelta(minutes=i * INTERVAL_MINUTES)
        hour_of_day = timestamp.hour + timestamp.minute / 60.0
        sun = _daylight_factor(hour_of_day)

        batch = []
        for rd in base_list:
            power = (rd.get("power_w") or 7708) * sun
            current = (rd.get("current_a") or 9.4) * sun
            voltage = rd.get("voltage_v") or rd.get("voltage") or 820

            batch.append({
                "string_id": rd.get("string_id", f"DEMO-STR-{len(batch)+1:03d}"),
                "voltage_v": voltage,
                "current_a": round(current, 2),
                "power_w": round(power, 1),
                "irradiance_wpm2": round(
                    (base_weather.get("irradiance_wpm2") or 850) * sun, 1,
                ),
                "temperature_c": round(
                    (base_weather.get("temperature_c") or 28) - 5 + 15 * sun, 1,
                ),
                "timestamp": timestamp.isoformat(),
            })

        await event_bus.publish(
            ReadingGenerated(readings=batch, weather={
                "temperature_c": batch[0]["temperature_c"],
                "humidity_pct": base_weather.get("humidity_pct"),
                "irradiance_wpm2": batch[0]["irradiance_wpm2"],
                "wind_speed_mps": base_weather.get("wind_speed_mps"),
                "wind_direction": base_weather.get("wind_direction"),
                "precipitation_mm": base_weather.get("precipitation_mm"),
                "description": "sunny" if sun > 0.5 else "cloudy" if sun > 0.2 else "night",
            }),
        )

    logger.info(
        "Demo mode: published %d historical ReadingGenerated events", STEPS,
    )
