from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from app.simulator.models import FaultConfig, StringStatus
from app.simulator.plant_config import PLANT, PlantConfig
from app.simulator.reading_generator import ReadingGenerator


class FaultEngine:
    """Decides *when* and *where* faults occur; delegates injection.

    The engine runs a schedule per cycle: it checks whether to start new
    faults, clear expired ones, or escalate existing conditions.  It never
    holds per-string state itself — the ``ReadingGenerator`` owns the
    actual fault flags.
    """

    def __init__(
        self,
        plant: PlantConfig = PLANT,
        config: FaultConfig | None = None,
        seed: int | None = None,
    ) -> None:
        self._plant = plant
        self._config = config or FaultConfig()
        self._rng = random.Random(seed)

        # Cycle counters for scheduled faults (keyed by string/inverter/sec)
        self._section_cycles: dict[str, int] = {}
        self._inverter_cycles: dict[str, int] = {}
        self._string_cycles: dict[str, int] = {}

        self._initialized = False

    # ------------------------------------------------------------------
    # Initialisation — seed the first batch of faults
    # ------------------------------------------------------------------

    def initialize(self, generator: ReadingGenerator) -> None:
        """Seed initial faults across the plant."""
        for sec_id in self._plant.section_ids():
            if self._config.section_outage and self._rng.random() < 0.005:
                cycles = self._rng.randint(6, 24)
                self._section_cycles[sec_id] = cycles
                generator.inject_section_outage(sec_id)

        for inv_id in self._plant.all_inverter_ids():
            if self._config.inverter_failure and self._rng.random() < 0.01:
                cycles = self._rng.randint(6, 36)
                self._inverter_cycles[inv_id] = cycles
                generator.inject_inverter_fault(inv_id)

        for string_id in self._plant.all_string_ids():
            if self._rng.random() < self._config.fault_probability:
                self._assign_string_fault(string_id, generator)

        self._initialized = True

    # ------------------------------------------------------------------
    # Per-cycle update
    # ------------------------------------------------------------------

    def update(self, dt: datetime, generator: ReadingGenerator) -> None:
        """Run one cycle of fault scheduling."""
        if not self._initialized:
            self.initialize(generator)

        self._update_section_faults(generator)
        self._update_inverter_faults(generator)
        self._update_string_faults(generator)

    def _update_section_faults(self, generator: ReadingGenerator) -> None:
        to_remove: list[str] = []
        for sec_id, cycles in self._section_cycles.items():
            remaining = cycles - 1
            if remaining <= 0:
                to_remove.append(sec_id)
            else:
                self._section_cycles[sec_id] = remaining

        for sec_id in to_remove:
            del self._section_cycles[sec_id]

        if self._config.section_outage and self._rng.random() < 0.0001:
            sec_id = self._rng.choice(self._plant.section_ids())
            if sec_id not in self._section_cycles:
                cycles = self._rng.randint(6, 24)
                self._section_cycles[sec_id] = cycles
                generator.inject_section_outage(sec_id)

    def _update_inverter_faults(self, generator: ReadingGenerator) -> None:
        to_remove: list[str] = []
        for inv_id, cycles in self._inverter_cycles.items():
            remaining = cycles - 1
            if remaining <= 0:
                to_remove.append(inv_id)
            else:
                self._inverter_cycles[inv_id] = remaining

        for inv_id in to_remove:
            del self._inverter_cycles[inv_id]

        if self._config.inverter_failure and self._rng.random() < 0.0002:
            inv_id = self._rng.choice(self._plant.all_inverter_ids())
            if inv_id not in self._inverter_cycles:
                cycles = self._rng.randint(6, 36)
                self._inverter_cycles[inv_id] = cycles
                generator.inject_inverter_fault(inv_id)

    def _update_string_faults(self, generator: ReadingGenerator) -> None:
        to_remove: list[str] = []
        for string_id, cycles in self._string_cycles.items():
            remaining = cycles - 1
            if remaining <= 0:
                to_remove.append(string_id)
                generator.clear_fault(string_id)
            else:
                self._string_cycles[string_id] = remaining

        for string_id in to_remove:
            del self._string_cycles[string_id]

        for string_id in self._plant.all_string_ids():
            if string_id not in self._string_cycles:
                if self._rng.random() < self._config.fault_probability / 6:
                    self._assign_string_fault(string_id, generator)

    # ------------------------------------------------------------------
    # Fault assignment
    # ------------------------------------------------------------------

    def _assign_string_fault(
        self, string_id: str, generator: ReadingGenerator
    ) -> None:
        """Pick a random string-level fault and inject it."""
        candidates: list[StringStatus] = []
        if self._config.dirty_panel:
            candidates.append(StringStatus.DIRTY_PANEL)
        if self._config.partial_shading:
            candidates.append(StringStatus.PARTIAL_SHADING)
        if self._config.disconnected_cable:
            candidates.append(StringStatus.DISCONNECTED)
        if self._config.open_circuit:
            candidates.append(StringStatus.OPEN_CIRCUIT)
        if self._config.sensor_failure:
            candidates.append(StringStatus.SENSOR_FAILURE)

        if not candidates:
            return

        fault = self._rng.choice(candidates)
        generator.inject_fault(string_id, fault)

        # Keep the schedule so we don't re-inject on the next cycle
        self._string_cycles[string_id] = 1

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, int]:
        """Return current fault counts (snapshot)."""
        return {
            "section_outages": len(self._section_cycles),
            "inverter_failures": len(self._inverter_cycles),
            "active_string_faults": len(self._string_cycles),
        }
