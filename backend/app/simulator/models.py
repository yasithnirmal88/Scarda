from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WeatherType(str, enum.Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORM = "storm"


class StringStatus(str, enum.Enum):
    HEALTHY = "Healthy"
    DIRTY_PANEL = "Dirty Panel"
    PARTIAL_SHADING = "Partial Shading"
    DISCONNECTED = "Disconnected"
    OPEN_CIRCUIT = "Open Circuit"
    DEGRADED = "Degraded"
    SENSOR_FAILURE = "Sensor Failure"
    INVERTER_FAILURE = "Inverter Failure"
    SECTION_OUTAGE = "Section Outage"


class FaultConfig(BaseModel):
    dirty_panel: bool = True
    partial_shading: bool = True
    disconnected_cable: bool = True
    open_circuit: bool = True
    string_degradation: bool = True
    sensor_failure: bool = True
    inverter_failure: bool = True
    section_outage: bool = True
    fault_probability: float = 0.03


class SimulatorConfig(BaseModel):
    seed: int | None = None
    interval_minutes: int = 10
    fault_config: FaultConfig = Field(default_factory=FaultConfig)


class WeatherState(BaseModel):
    weather_type: WeatherType = WeatherType.SUNNY
    irradiance_multiplier: float = 1.0
    description: str = "Clear skies"
    temperature_base: float = 30.0
    humidity_base: float = 60.0
    wind_speed_base: float = 5.0


class StringReading(BaseModel):
    timestamp: datetime
    section_id: str
    inverter_id: str
    string_id: str
    voltage: float
    current: float
    power: float
    irradiance: float
    ambient_temperature: float
    panel_temperature: float
    status: str

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def to_csv_row(self) -> list[str]:
        return [
            self.timestamp.isoformat(),
            self.section_id,
            self.inverter_id,
            self.string_id,
            f"{self.voltage:.2f}",
            f"{self.current:.3f}",
            f"{self.power:.2f}",
            f"{self.irradiance:.2f}",
            f"{self.ambient_temperature:.2f}",
            f"{self.panel_temperature:.2f}",
            self.status,
        ]

    @staticmethod
    def csv_header() -> list[str]:
        return [
            "timestamp", "section_id", "inverter_id", "string_id",
            "voltage", "current", "power", "irradiance",
            "ambient_temperature", "panel_temperature", "status",
        ]


class SimulatorSummary(BaseModel):
    total_readings: int
    healthy_count: int
    faulted_count: int
    weather_summary: str
    total_power_kw: float
    total_energy_kwh: float
