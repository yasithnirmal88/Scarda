from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from simulator.exporters import export_csv, export_json
from simulator.fault_engine import FaultEngine
from simulator.models import FaultConfig, SimulatorConfig, SimulatorSummary, StringReading
from simulator.plant_config import PLANT, PlantConfig
from simulator.reading_generator import ReadingGenerator
from simulator.time_engine import TimeEngine
from simulator.weather_engine import WeatherEngine


class SimulationController:
    """Orchestrates the entire stateful solar-farm simulation.

    Components
    ----------
    - ``TimeEngine``   — timestamp generation
    - ``WeatherEngine`` — irradiance / weather  (stateful)
    - ``FaultEngine``   — fault scheduling      (stateful)
    - ``ReadingGenerator`` — per-string state   (stateful)

    All state is retained between ``generate_*()`` calls so repeated
    invocations produce a continuous timeline.
    """

    def __init__(
        self,
        config: SimulatorConfig | None = None,
        plant: PlantConfig = PLANT,
    ) -> None:
        self._config = config or SimulatorConfig()
        self._plant = plant

        if self._config.seed is not None:
            random.seed(self._config.seed)

        rs = self._config.seed
        self._weather = WeatherEngine(seed=rs)
        self._time = TimeEngine(interval_minutes=self._config.interval_minutes)
        self._reader = ReadingGenerator(
            plant=plant, weather_engine=self._weather, seed=rs,
        )
        self._fault = FaultEngine(
            plant=plant, config=self._config.fault_config, seed=rs,
        )
        self._fault.initialize(self._reader)

    # --- public accessors ---------------------------------------------------

    @property
    def plant(self) -> PlantConfig:
        return self._plant

    @property
    def weather_engine(self) -> WeatherEngine:
        return self._weather

    @property
    def fault_engine(self) -> FaultEngine:
        return self._fault

    @property
    def reading_generator(self) -> ReadingGenerator:
        return self._reader

    # --- single-cycle generation -------------------------------------------

    def generate_reading(self, dt: datetime | None = None) -> list[StringReading]:
        """Generate one complete set of readings at *dt* (default: now)."""
        ts = dt or datetime.now()
        self._fault.update(ts, self._reader)
        return self._reader.generate(ts)

    # --- multi-cycle generation --------------------------------------------

    def generate_day(self, day: datetime | None = None) -> list[StringReading]:
        """Generate readings for a full 24-hour period.

        State evolves continuously across timesteps so the plant behaves
        like a real installation, not a fresh random draw per step.
        """
        all_readings: list[StringReading] = []
        for ts in self._time.generate_day(day):
            all_readings.extend(self.generate_reading(ts))
        return all_readings

    def generate_week(self, week_start: datetime | None = None) -> list[StringReading]:
        """Generate readings for 7 consecutive days."""
        all_readings: list[StringReading] = []
        for ts in self._time.generate_week(week_start):
            all_readings.extend(self.generate_reading(ts))
        return all_readings

    def generate_custom(self, hours: float) -> list[StringReading]:
        """Generate readings for a custom number of hours from now."""
        all_readings: list[StringReading] = []
        for ts in self._time.generate_custom(int(hours)):
            all_readings.extend(self.generate_reading(ts))
        return all_readings

    # --- IDataProvider-compatible methods -----------------------------------

    async def get_current_readings(self) -> dict[str, Any]:
        """Return current readings for the whole plant."""
        readings = self.generate_reading()
        return {
            "total_power_kw": round(sum(r.power for r in readings) / 1000.0, 2),
            "daily_energy_kwh": 0.0,
            "active_inverters": self._plant.total_inverters,
            "total_inverters": self._plant.total_inverters,
            "readings": [r.to_dict() for r in readings],
            "timestamp": datetime.now().isoformat(),
        }

    async def get_weather(self) -> dict[str, Any]:
        """Return current weather conditions."""
        weather = self._weather.get_weather(datetime.now())
        irr = self._weather.effective_irradiance(datetime.now())
        return {
            "temperature_c": weather.temperature_base,
            "humidity_pct": weather.humidity_base,
            "irradiance_wpm2": round(irr, 2),
            "wind_speed_mps": weather.wind_speed_base,
            "wind_direction": self._random_wind_dir(),
            "precipitation_mm": round(
                0.0 if weather.weather_type.value == "sunny"
                else random.uniform(0, 5), 2,
            ),
            "description": weather.description,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_historical_readings(
        self, start: datetime, end: datetime,
    ) -> list[dict[str, Any]]:
        """Return historical string readings within a time range."""
        all_readings: list[StringReading] = []
        for ts in self._time.generate_timestamps(start, end):
            all_readings.extend(self.generate_reading(ts))
        return [r.to_dict() for r in all_readings]

    async def get_historical_weather(
        self, start: datetime, end: datetime,
    ) -> list[dict[str, Any]]:
        """Return historical weather data within a time range."""
        records: list[dict[str, Any]] = []
        for ts in self._time.generate_timestamps(start, end):
            w = self._weather.get_weather(ts)
            irr = self._weather.effective_irradiance(ts)
            records.append({
                "timestamp": ts.isoformat(),
                "temperature_c": w.temperature_base,
                "humidity_pct": w.humidity_base,
                "irradiance_wpm2": round(irr, 2),
                "wind_speed_mps": w.wind_speed_base,
                "weather_type": w.weather_type.value,
            })
        return records

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "provider": "simulator",
            "connected": True,
            "total_strings": self._plant.total_strings,
            "total_inverters": self._plant.total_inverters,
        }

    @staticmethod
    def _random_wind_dir() -> str:
        dirs = [
            "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
        ]
        return random.choice(dirs)

    # --- export helpers -----------------------------------------------------

    def export_json(self, readings: list[StringReading], filepath: str) -> None:
        export_json(readings, filepath)

    def export_csv(self, readings: list[StringReading], filepath: str) -> None:
        export_csv(readings, filepath)

    # --- summary ------------------------------------------------------------

    def summarize(self, readings: list[StringReading]) -> SimulatorSummary:
        """Compute summary statistics over a set of readings."""
        if not readings:
            return SimulatorSummary(
                total_readings=0, healthy_count=0, faulted_count=0,
                weather_summary="N/A", total_power_kw=0.0, total_energy_kwh=0.0,
            )

        us = self._plant.total_strings
        steps = max(len(readings) // us, 1)
        latest = readings[-us:]

        healthy = sum(1 for r in readings if r.status == "Healthy")
        faulted = len(readings) - healthy
        inst_power_kw = sum(r.power for r in latest) / 1000.0

        total_power = sum(r.power for r in readings)
        interval_hours = self._config.interval_minutes / 60.0
        avg_power_per_step = total_power / steps / 1000.0
        energy = avg_power_per_step * interval_hours * steps

        weather = self._weather.get_weather(datetime.now())

        return SimulatorSummary(
            total_readings=len(readings),
            healthy_count=healthy,
            faulted_count=faulted,
            weather_summary=weather.description,
            total_power_kw=round(inst_power_kw, 2),
            total_energy_kwh=round(energy, 2),
        )
