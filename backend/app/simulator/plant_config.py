from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlantConfig:
    num_sections: int = 4
    inverters_per_section: int = 9
    strings_per_inverter: int = 24

    @property
    def total_inverters(self) -> int:
        return self.num_sections * self.inverters_per_section

    @property
    def total_strings(self) -> int:
        return self.total_inverters * self.strings_per_inverter

    def section_ids(self) -> list[str]:
        return [f"SEC{str(i + 1).zfill(2)}" for i in range(self.num_sections)]

    def inverter_ids(self, section_idx: int) -> list[str]:
        sec = f"SEC{str(section_idx + 1).zfill(2)}"
        return [
            f"{sec}-INV{str(i + 1).zfill(2)}"
            for i in range(self.inverters_per_section)
        ]

    def all_inverter_ids(self) -> list[str]:
        result: list[str] = []
        for sec_idx in range(self.num_sections):
            result.extend(self.inverter_ids(sec_idx))
        return result

    def string_ids(self, section_idx: int, inverter_idx: int) -> list[str]:
        inv = self.inverter_ids(section_idx)[inverter_idx]
        return [
            f"{inv}-STR{str(i + 1).zfill(2)}"
            for i in range(self.strings_per_inverter)
        ]

    def all_string_ids(self) -> list[str]:
        result: list[str] = []
        for sec_idx in range(self.num_sections):
            for inv_idx in range(self.inverters_per_section):
                result.extend(self.string_ids(sec_idx, inv_idx))
        return result

    def section_for_string(self, string_id: str) -> str:
        return string_id[:5]

    def inverter_for_string(self, string_id: str) -> str:
        return string_id.rsplit("-", 1)[0]

    def section_and_inverter_for_string(self, string_id: str) -> tuple[str, str]:
        return string_id[:5], string_id[:10]


PLANT = PlantConfig()
