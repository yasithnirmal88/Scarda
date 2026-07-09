from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.providers.interfaces import IDataProvider
from app.repositories.alert_repository import AlertRepository
from app.repositories.reading_repository import ReadingRepository
from app.repositories.string_repository import StringRepository
from app.repositories.inverter_repository import InverterRepository
from app.repositories.section_repository import SectionRepository
from app.repositories.weather_repository import WeatherRepository


class DashboardService:
    """Aggregates real-time data into a single dashboard response.

    Combines current readings, weather, active alerts, and plant
    statistics into one structured payload.  All data sources are
    injected — no hard coupling to any provider or repository.
    """

    def __init__(
        self,
        provider: IDataProvider,
        db: Session,
    ) -> None:
        self._provider = provider
        self._reading_repo = ReadingRepository(db)
        self._weather_repo = WeatherRepository(db)
        self._alert_repo = AlertRepository(db)
        self._string_repo = StringRepository(db)
        self._inverter_repo = InverterRepository(db)
        self._section_repo = SectionRepository(db)

    async def get_dashboard(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start.replace(day=1)

        readings_data = await self._provider.get_current_readings()
        weather_data = await self._provider.get_weather()

        alerts = self._alert_repo.find_all()
        active_alerts = [a for a in alerts if getattr(a, "status", "active") == "active"]

        total_power = readings_data.get("total_power_kw", 0.0)
        daily_energy = self._reading_repo.total_energy_between(today_start, now)
        weekly_energy = self._reading_repo.total_energy_between(week_start, now)
        monthly_energy = self._reading_repo.total_energy_between(month_start, now)

        peak_power = self._reading_repo.peak_power_between(today_start, now)

        strings = self._string_repo.find_all()
        inverters = self._inverter_repo.find_all()
        sections = self._section_repo.find_all()

        return {
            "power": {
                "total_power_kw": total_power,
                "daily_energy_kwh": round(daily_energy, 2),
                "weekly_energy_kwh": round(weekly_energy, 2),
                "monthly_energy_kwh": round(monthly_energy, 2),
                "peak_power_kw": round(peak_power, 2) if peak_power else None,
            },
            "plant": {
                "total_sections": len(sections),
                "total_inverters": len(inverters),
                "total_strings": len(strings),
                "active_inverters": readings_data.get("active_inverters", 0),
            },
            "weather": {
                "temperature_c": weather_data.get("temperature_c"),
                "humidity_pct": weather_data.get("humidity_pct"),
                "irradiance_wpm2": weather_data.get("irradiance_wpm2"),
                "wind_speed_mps": weather_data.get("wind_speed_mps"),
                "wind_direction": weather_data.get("wind_direction"),
                "precipitation_mm": weather_data.get("precipitation_mm"),
                "description": weather_data.get("description"),
            },
            "alerts": {
                "total": len(active_alerts),
                "critical": sum(
                    1 for a in active_alerts if getattr(a, "severity", None) == "critical"
                ),
                "warning": sum(
                    1 for a in active_alerts if getattr(a, "severity", None) == "warning"
                ),
                "info": sum(
                    1 for a in active_alerts if getattr(a, "severity", None) == "info"
                ),
            },
            "timestamp": now.isoformat(),
        }