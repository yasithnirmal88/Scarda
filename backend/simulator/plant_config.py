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
        ids: list[str] = []
        for sec_idx in range(self.num_sections):
            ids.extend(self.inverter_ids(sec_idx))
        return ids

    def string_ids(self, section_idx: int, inverter_idx: int) -> list[str]:
        sec = f"SEC{str(section_idx + 1).zfill(2)}"
        inv = f"INV{str(inverter_idx + 1).zfill(2)}"
        return [
            f"{sec}-{inv}-STR{str(i + 1).zfill(2)}"
            for i in range(self.strings_per_inverter)
        ]

    def all_string_ids(self) -> list[str]:
        ids: list[str] = []
        for sec_idx in range(self.num_sections):
            for inv_idx in range(self.inverters_per_section):
                ids.extend(self.string_ids(sec_idx, inv_idx))
        return ids

    def section_for_string(self, string_id: str) -> str:
        return string_id.split("-")[0]

    def inverter_for_string(self, string_id: str) -> str:
        parts = string_id.split("-")
        return f"{parts[0]}-{parts[1]}"

    def inverter_ids_for_section(self, section_id: str) -> list[str]:
        sec_idx = int(section_id.replace("SEC", "")) - 1
        return self.inverter_ids(sec_idx)

    def string_ids_for_inverter(self, inverter_id: str) -> list[str]:
        parts = inverter_id.split("-")
        sec_idx = int(parts[0].replace("SEC", "")) - 1
        inv_idx = int(parts[1].replace("INV", "")) - 1
        return self.string_ids(sec_idx, inv_idx)


PLANT = PlantConfig()
