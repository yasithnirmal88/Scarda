"""Stateful per-string reading generator.

Maintains a ``StringState`` for each PV string across generation cycles.
Values evolve smoothly with slew-rate limiting, thermal inertia, and
slow degradation accumulation. Fault injection is handled externally
by the ``FaultEngine``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime

from simulator.models import StringReading, StringStatus
from simulator.plant_config import PLANT, PlantConfig
from simulator.weather_engine import WeatherEngine


# ---------------------------------------------------------------------------
# Per-string state — persisted across every generation cycle
# ---------------------------------------------------------------------------


@dataclass
class StringState:
    """Stateful representation of one PV string that evolves over time.

    Every field is the *actual* value at the last simulated timestamp.
    On each cycle these values move smoothly toward their targets.
    """

    string_id: str
    section_id: str
    inverter_id: str

    # --- electrical outputs (actual) ----------------------------------------
    voltage: float = 0.0
    current: float = 0.0
    power: float = 0.0

    # --- temperatures -------------------------------------------------------
    panel_temperature: float = 25.0

    # --- intrinsic capacity (drifts over hours / days) --------------------
    base_voltage: float = 820.0
    base_current_capacity: float = 9.5

    # --- fault / degradation ----------------------------------------------
    fault: StringStatus = StringStatus.HEALTHY
    degradation_level: float = 0.0  # 0 = pristine, 1 = total loss
    fault_cycles_remaining: int = 0  # how many more cycles this fault lasts

    # --- current target (set during step) for diagnostics -----------------
    _target_voltage: float = 0.0
    _target_current: float = 0.0


# ---------------------------------------------------------------------------
# Slew-rate limiter — smooth transitions
# ---------------------------------------------------------------------------


def _slew(value: float, target: float, max_up: float, max_down: float) -> float:
    """Move *value* toward *target* at a bounded rate.

    Parameters
    ----------
    max_up : float
        Maximum increase per cycle.
    max_down : float
        Maximum decrease per cycle.
    """
    if target > value:
        return value + min(target - value, max_up)
    return value - min(value - target, max_down)


def _drift(value: float, center: float, step: float, rng: random.Random) -> float:
    """Random walk around *center* with a mean-reverting pull.

    Parameters
    ----------
    rng : random.Random
        Seeded RNG instance for deterministic behavior.
    """
    diff = center - value
    MEAN_REVERT_PULL = 0.002  # very gentle pull toward centre
    pull = diff * MEAN_REVERT_PULL
    noise = rng.uniform(-step, step)
    return value + pull + noise


# ---------------------------------------------------------------------------
# Reading generator — stateful core
# ---------------------------------------------------------------------------


class ReadingGenerator:
    """Generates realistic readings by evolving per-string state.

    Each ``StringState`` persists across calls so the plant behaves like
    a real installation: values ramp smoothly, faults linger, degradation
    accumulates.
    """

    # Slew rates (per 10-min interval)
    V_MAX_UP = 15.0       # Volts / cycle during ramp-up
    V_MAX_DOWN = 20.0     # Volts / cycle during normal operation

    # When target is 0 V (night / fault) drop much faster
    V_MAX_DOWN_ZERO = 300.0
    I_MAX_UP = 0.6       # Amps   / cycle
    I_MAX_DOWN = 0.8
    T_MAX_UP = 1.2       # °C     / cycle
    T_MAX_DOWN = 0.8

    # Electrical baseline targets
    BASE_VOLTAGE_TARGET = 820.0
    BASE_CURRENT_TARGET = 9.5
    BASE_VOLTAGE_MIN = 700.0
    BASE_VOLTAGE_MAX = 950.0
    BASE_CURRENT_MIN = 6.0
    BASE_CURRENT_MAX = 12.0

    # Irradiance normalization reference
    IRRADIANCE_REFERENCE = 1000.0

    # Voltage scaling with irradiance
    V_FRACTION_LOW = 0.85
    V_FRACTION_HIGH = 0.15
    V_OPEN_CIRCUIT_MULT = 1.15

    # Fault multipliers for current
    DIRTY_PANEL_I_MIN = 0.60
    DIRTY_PANEL_I_MAX = 0.80
    SHADING_I_MIN = 0.50
    SHADING_I_MAX = 0.85

    # Degradation thresholds
    DEGRADATION_PROBABILITY = 0.0005  # ~ once per 2000 cycles (~14 days)
    DEGRADATION_MIN = 0.01
    DEGRADATION_MAX = 0.05

    # Panel temperature offset range
    PANEL_TEMP_OFFSET_MIN = 8.0
    PANEL_TEMP_OFFSET_MAX = 18.0

    # Default fault durations (cycles)
    FAULT_DURATIONS: dict[StringStatus, tuple[int, int]] = {
        StringStatus.DIRTY_PANEL: (6, 48),
        StringStatus.PARTIAL_SHADING: (3, 24),
        StringStatus.DISCONNECTED: (12, 72),
        StringStatus.OPEN_CIRCUIT: (6, 36),
        StringStatus.SENSOR_FAILURE: (1, 6),
    }
    DEFAULT_FAULT_DURATION = 6

    def __init__(
        self,
        plant: PlantConfig = PLANT,
        weather_engine: WeatherEngine | None = None,
        seed: int | None = None,
    ) -> None:
        self._plant = plant
        self._weather = weather_engine or WeatherEngine(seed=seed)
        self._rng = random.Random(seed)

        # State dictionary — survives across generation calls
        self._state: dict[str, StringState] = {}
        self._initialized = False

    def _init_state(self) -> None:
        if self._initialized:
            return

        for string_id in self._plant.all_string_ids():
            self._state[string_id] = StringState(
                string_id=string_id,
                section_id=self._plant.section_for_string(string_id),
                inverter_id=self._plant.inverter_for_string(string_id),
                voltage=0.0,
                current=0.0,
                power=0.0,
                panel_temperature=25.0,
                base_voltage=round(self._rng.uniform(780, 860), 1),
                base_current_capacity=round(self._rng.uniform(8.0, 10.5), 3),
                fault=StringStatus.HEALTHY,
                degradation_level=0.0,
                fault_cycles_remaining=0,
            )

        self._initialized = True

    @property
    def state(self) -> dict[str, StringState]:
        """Expose the state dictionary for external inspection / injection."""
        return self._state

    # ------------------------------------------------------------------
    # Public generation methods
    # ------------------------------------------------------------------

    def generate(self, dt: datetime) -> list[StringReading]:
        """Step every string forward by one interval and return readings."""
        self._init_state()

        irr = self._weather.effective_irradiance(dt)
        weather = self._weather.get_weather(dt)
        irr_fraction = irr / self.IRRADIANCE_REFERENCE
        is_day = irr > 1.0

        readings: list[StringReading] = []

        for string_id in self._plant.all_string_ids():
            st = self._state[string_id]

            self._step_electrical(st, irr_fraction, is_day, weather.temperature_base)
            self._step_temperature(st, irr_fraction, weather.temperature_base)
            self._step_fault(st)
            self._step_degradation(st)

            readings.append(
                StringReading(
                    timestamp=dt,
                    section_id=st.section_id,
                    inverter_id=st.inverter_id,
                    string_id=st.string_id,
                    voltage=round(st.voltage, 1),
                    current=round(st.current, 3),
                    power=round(st.power, 2),
                    irradiance=round(irr, 2),
                    ambient_temperature=round(weather.temperature_base, 1),
                    panel_temperature=round(st.panel_temperature, 1),
                    status=st.fault.value,
                )
            )

        return readings

    # ------------------------------------------------------------------
    # Internal step methods
    # ------------------------------------------------------------------

    def _step_electrical(
        self,
        st: StringState,
        irr_fraction: float,
        is_day: bool,
        ambient: float,
    ) -> None:
        """Compute target electrical values and slew toward them."""
        if not is_day:
            st._target_voltage = 0.0
            st._target_current = 0.0
        else:
            # Voltage is fairly flat across irradiance; drops slightly at low irr
            v_target = st.base_voltage * (self.V_FRACTION_LOW + self.V_FRACTION_HIGH * irr_fraction)
            # Current is proportional to irradiance
            i_target = st.base_current_capacity * irr_fraction

            # Degradation reduces current proportionally
            i_target *= 1.0 - st.degradation_level

            # Fault overrides
            if st.fault == StringStatus.DISCONNECTED:
                v_target = 0.0
                i_target = 0.0
            elif st.fault == StringStatus.OPEN_CIRCUIT:
                v_target = st.base_voltage * self.V_OPEN_CIRCUIT_MULT  # voltage rises
                i_target = 0.0
            elif st.fault == StringStatus.DIRTY_PANEL:
                i_target *= self._rng.uniform(self.DIRTY_PANEL_I_MIN, self.DIRTY_PANEL_I_MAX)
            elif st.fault == StringStatus.PARTIAL_SHADING:
                i_target *= self._rng.uniform(self.SHADING_I_MIN, self.SHADING_I_MAX)

            st._target_voltage = v_target
            st._target_current = i_target

        # Slew-rate-limited movement (faster drop to zero for night / faults)
        v_down = self.V_MAX_DOWN_ZERO if st._target_voltage == 0.0 else self.V_MAX_DOWN
        st.voltage = _slew(st.voltage, st._target_voltage, self.V_MAX_UP, v_down)

        i_down = self.I_MAX_DOWN
        st.current = _slew(st.current, st._target_current, self.I_MAX_UP, i_down)
        st.power = st.voltage * st.current

        # Drift intrinsic capacity very slowly (over days)
        st.base_voltage = _drift(st.base_voltage, self.BASE_VOLTAGE_TARGET, 0.3, self._rng)
        st.base_current_capacity = _drift(st.base_current_capacity, self.BASE_CURRENT_TARGET, 0.01, self._rng)
        st.base_voltage = max(self.BASE_VOLTAGE_MIN, min(self.BASE_VOLTAGE_MAX, st.base_voltage))
        st.base_current_capacity = max(self.BASE_CURRENT_MIN, min(self.BASE_CURRENT_MAX, st.base_current_capacity))

    def _step_temperature(
        self, st: StringState, irr_fraction: float, ambient: float
    ) -> None:
        """Panel temperature lags behind irradiance with thermal inertia."""
        panel_offset = self._rng.uniform(self.PANEL_TEMP_OFFSET_MIN, self.PANEL_TEMP_OFFSET_MAX)
        target_temp = ambient + panel_offset * irr_fraction
        st.panel_temperature = _slew(
            st.panel_temperature, target_temp, self.T_MAX_UP, self.T_MAX_DOWN
        )

    def _step_fault(self, st: StringState) -> None:
        """Count down fault duration; clear fault when it expires."""
        if st.fault is not StringStatus.HEALTHY:
            st.fault_cycles_remaining -= 1
            if st.fault_cycles_remaining <= 0:
                st.fault = StringStatus.HEALTHY
                st.fault_cycles_remaining = 0

    def _step_degradation(self, st: StringState) -> None:
        """Slowly accumulate irreversible degradation."""
        if self._rng.random() < self.DEGRADATION_PROBABILITY:
            st.degradation_level = min(1.0, st.degradation_level + self._rng.uniform(self.DEGRADATION_MIN, self.DEGRADATION_MAX))

    # ------------------------------------------------------------------
    # Fault injection (called externally by FaultEngine)
    # ------------------------------------------------------------------

    def inject_fault(
        self,
        string_id: str,
        fault: StringStatus,
        duration_cycles: int | None = None,
    ) -> None:
        """Apply a fault to a string. Overwrites any existing fault."""
        st = self._state.get(string_id)
        if st is None:
            return

        st.fault = fault
        if duration_cycles is not None:
            st.fault_cycles_remaining = duration_cycles
        elif fault in self.FAULT_DURATIONS:
            lo, hi = self.FAULT_DURATIONS[fault]
            st.fault_cycles_remaining = self._rng.randint(lo, hi)
        else:
            st.fault_cycles_remaining = self.DEFAULT_FAULT_DURATION

    def inject_inverter_fault(self, inverter_id: str) -> None:
        """Fault every string under an inverter."""
        for string_id in self._plant.string_ids(
            *self._parse_inverter(inverter_id)
        ):
            self.inject_fault(string_id, StringStatus.INVERTER_FAILURE, 6)

    def inject_section_outage(self, section_id: str) -> None:
        """Fault every string in a section."""
        sec_idx = int(section_id.replace("SEC", "")) - 1
        for inv_idx in range(self._plant.inverters_per_section):
            for string_id in self._plant.string_ids(sec_idx, inv_idx):
                self.inject_fault(string_id, StringStatus.SECTION_OUTAGE, 6)

    def clear_fault(self, string_id: str) -> None:
        """Manually clear a fault."""
        st = self._state.get(string_id)
        if st is not None:
            st.fault = StringStatus.HEALTHY
            st.fault_cycles_remaining = 0

    @staticmethod
    def _parse_inverter(inverter_id: str) -> tuple[int, int]:
        """Parse ``SEC01-INV01`` → ``(section_idx, inverter_idx)``."""
        parts = inverter_id.split("-")
        sec = int(parts[0].replace("SEC", "")) - 1
        inv = int(parts[1].replace("INV", "")) - 1
        return sec, inv
