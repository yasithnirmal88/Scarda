"""Demo: simulate 24 hours with fully stateful per-string evolution."""

from datetime import datetime

from app.simulator.models import SimulatorConfig
from app.simulator.simulation_controller import SimulationController


def _print_sep(char: str = "=", width: int = 68) -> None:
    print(char * width)


def main() -> None:
    config = SimulatorConfig(seed=42, interval_minutes=10)
    sim = SimulationController(config=config)

    _print_sep()
    print("  Solar AIM — Stateful Solar Farm Simulator")
    print(f"  Plant:  {sim.plant.num_sections} sections  |  "
          f"{sim.plant.total_inverters} inverters  |  "
          f"{sim.plant.total_strings} strings")
    print(f"  Every string remembers its V, I, T, fault & degradation across cycles")
    _print_sep()

    # ---- Run 24-hour simulation -------------------------------------------
    t0 = datetime.now()
    readings = sim.generate_day()
    elapsed = datetime.now() - t0

    us = sim.plant.total_strings
    steps = len(readings) // us
    summary = sim.summarize(readings)
    fault_info = sim.fault_engine.summary()

    print(f"\n  Generated {len(readings):,} readings in {elapsed.total_seconds():.2f}s")
    print(f"  Timesteps:  {steps}  (every {config.interval_minutes} min)")
    print(f"  Weather:    {summary.weather_summary}")
    print(f"  Health:     {summary.healthy_count:,} healthy  |  "
          f"{summary.faulted_count:,} faulted  "
          f"({summary.faulted_count / max(summary.total_readings,1)*100:.2f}%)")
    print(f"  Faults now: {fault_info['section_outages']} section, "
          f"{fault_info['inverter_failures']} inverter, "
          f"{fault_info['active_string_faults']} string")

    # ---- Show stateful evolution of the same string across the day --------

    target_string = "SEC01-INV01-STR01"
    idx = [i for i, r in enumerate(readings) if r.string_id == target_string]
    samples = [readings[i] for i in idx]

    _print_sep("-")
    print(f"  Stateful evolution of {target_string} across 24 h:\n")
    print(f"  {'Time':>6}  {'V':>7}  {'I':>6}  {'P':>8}  "
          f"{'Irr':>6}  {'T_panel':>7}  {'Status':>18}")
    print(f"  {'-'*6}  {'-'*7}  {'-'*6}  {'-'*8}  "
          f"{'-'*6}  {'-'*7}  {'-'*18}")

    for s in samples:
        if s.timestamp.hour in (0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 23):
            print(f"  {s.timestamp:%H:%M}  {s.voltage:>7.1f}  {s.current:>6.3f}  "
                  f"{s.power:>8.2f}  {s.irradiance:>6.1f}  "
                  f"{s.panel_temperature:>7.1f}  {s.status:>18}")

    # ---- Show smooth ramping (dawn) for the same string -------------------

    dawn_readings = [s for s in samples if 5 <= s.timestamp.hour <= 8]
    if dawn_readings:
        _print_sep("-")
        print(f"  Dawn ramp (slew-rate-limited) for {target_string}:\n")
        print(f"  {'Time':>6}  {'V':>7}  {'I':>6}  {'P':>8}  "
              f"{'Irr':>6}  {'dI/dt':>7}")
        for i in range(1, len(dawn_readings)):
            prev = dawn_readings[i - 1]
            cur = dawn_readings[i]
            di = (cur.current - prev.current) * 6  # per-minute rate × 6 → per-hour
            print(f"  {cur.timestamp:%H:%M}  {cur.voltage:>7.1f}  {cur.current:>6.3f}  "
                  f"{cur.power:>8.2f}  {cur.irradiance:>6.1f}  {di:>+7.3f} A/h")

    # ---- Fault examples ---------------------------------------------------
    faulted = [r for r in readings if r.status != "Healthy"]
    if faulted:
        _print_sep("-")
        print(f"  Sample faulted readings ({len(faulted)} total):\n")
        shown: set[str] = set()
        for r in faulted:
            key = f"{r.timestamp:%H:%M}-{r.string_id}"
            if key not in shown and len(shown) < 6:
                shown.add(key)
                print(f"  {r.timestamp:%H:%M}  {r.string_id}  "
                      f"{r.voltage:>7.1f} V  {r.current:>6.3f} A  "
                      f"{r.power:>8.2f} W  [{r.status}]")

    # ---- Summary power ----------------------------------------------------
    _print_sep()
    print(f"  Power (latest timestep):  {summary.total_power_kw:>10.2f} kW")
    print(f"  Estimated daily energy:   {summary.total_energy_kwh:>10.2f} kWh")
    _print_sep()
    print()


if __name__ == "__main__":
    main()
