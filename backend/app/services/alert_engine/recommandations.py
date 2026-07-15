RECOMMENDATIONS: dict[str, str] = {
    "current_low": "Inspect panel for dirt, shading, or soiling.",
    "voltage_low": "Check string cable connections and junction boxes.",
    "voltage_zero": "Inspect fuse, disconnect switch, and wiring continuity.",
    "power_low": "Verify string performance — check panels, wiring, and inverter input.",
    "offline": "Verify communication with inverter and check DC isolator.",
    "communication_failure": "Check RS485/ethernet connection and inverter power.",
    "current_zero": "Check fuse, string fuse holder, and string connection.",
    "voltage_spike": "Inspect for loose neutral connections or lightning damage.",
}


def get_recommendation(rule_name: str) -> str:
    return RECOMMENDATIONS.get(rule_name, "Investigate anomaly and perform diagnostic check.")
