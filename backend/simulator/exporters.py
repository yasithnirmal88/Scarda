from __future__ import annotations

import csv
import json
from datetime import datetime
from typing import Any

from simulator.models import StringReading


def export_json(readings: list[StringReading], filepath: str) -> None:
    """Export a list of readings to a JSON file.

    Each reading is serialised as a flat dictionary. The file contains
    a single JSON array of objects.
    """
    data = [r.to_dict() for r in readings]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def export_csv(readings: list[StringReading], filepath: str) -> None:
    """Export a list of readings to a CSV file.

    The first row is a header. Each subsequent row is one reading.
    """
    if not readings:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(StringReading.csv_header())
        return

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(StringReading.csv_header())
        for r in readings:
            writer.writerow(r.to_csv_row())


def readings_to_dicts(readings: list[StringReading]) -> list[dict[str, Any]]:
    """Return readings as a list of plain dictionaries."""
    return [r.to_dict() for r in readings]
