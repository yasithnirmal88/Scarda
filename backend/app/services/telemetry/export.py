from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.reading_repository import ReadingRepository
from app.repositories.weather_repository import WeatherRepository


class ExportService:
    """Exports telemetry data in CSV, JSON, or other formats.

    All methods accept raw data dicts so they can be used both with
    repository queries and with pre-computed aggregations.  PDF is
    a placeholder for future integration with a PDF generation library.
    """

    def __init__(self, db: Session) -> None:
        self._reading_repo = ReadingRepository(db)
        self._weather_repo = WeatherRepository(db)

    async def readings_csv(
        self, start: datetime, end: datetime,
    ) -> str:
        readings = self._reading_repo.find_between(start, end)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "timestamp", "string_id", "voltage_v", "current_a",
            "power_w", "irradiance_wpm2", "temperature_c",
        ])
        for r in readings:
            writer.writerow([
                r.recorded_at.isoformat() if r.recorded_at else "",
                r.string_id,
                r.voltage, r.current, r.power,
                r.irradiance, r.temperature,
            ])
        return output.getvalue()

    async def readings_json(
        self, start: datetime, end: datetime,
    ) -> str:
        readings = self._reading_repo.find_between(start, end)
        data = [
            {
                "timestamp": r.recorded_at.isoformat() if r.recorded_at else None,
                "string_id": r.string_id,
                "voltage_v": r.voltage,
                "current_a": r.current,
                "power_w": r.power,
                "irradiance_wpm2": r.irradiance,
                "temperature_c": r.temperature,
            }
            for r in readings
        ]
        return json.dumps(data, indent=2, default=str)

    async def weather_csv(self, start: datetime, end: datetime) -> str:
        records = self._weather_repo.find_between(start, end)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "timestamp", "temperature_c", "humidity_pct",
            "irradiance_wpm2", "wind_speed_mps", "precipitation_mm",
        ])
        for r in records:
            writer.writerow([
                r.recorded_at.isoformat() if r.recorded_at else "",
                r.temperature, r.humidity, r.irradiance,
                r.wind_speed, r.precipitation,
            ])
        return output.getvalue()

    async def weather_json(self, start: datetime, end: datetime) -> str:
        records = self._weather_repo.find_between(start, end)
        data = [
            {
                "timestamp": r.recorded_at.isoformat() if r.recorded_at else None,
                "temperature_c": r.temperature,
                "humidity_pct": r.humidity,
                "irradiance_wpm2": r.irradiance,
                "wind_speed_mps": r.wind_speed,
                "precipitation_mm": r.precipitation,
            }
            for r in records
        ]
        return json.dumps(data, indent=2, default=str)

    async def export_pdf(self, data: list[dict[str, Any]], title: str = "Report") -> bytes:
        """Placeholder for future PDF export.

        When a PDF library is integrated (e.g. ReportLab, WeasyPrint),
        this method will render ``data`` into a formatted PDF document.
        """
        _ = data, title
        raise NotImplementedError("PDF export is not yet implemented")