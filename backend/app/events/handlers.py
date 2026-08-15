from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.events.event_bus import EventBus
from app.events.events import (
    AlertCreated,
    AlertResolved,
    DashboardRefresh,
    Event,
    ReadingGenerated,
    ReadingStored,
    SchedulerTick,
    WeatherUpdated,
)
from app.providers.interfaces import IDataProvider
from app.services.alert_engine.types import Reading as AlertReading
from app.websocket.broadcaster import Broadcaster

logger = logging.getLogger(__name__)


def _get_reading_repo():
    from app.database.migrations import is_database_available
    from app.repositories.reading_repository import ReadingRepository

    if not is_database_available():
        return None, None
    try:
        from app.database import get_db

        db = next(get_db())
        return ReadingRepository(db), db
    except Exception:
        return None, None


def _get_weather_repo():
    from app.database.migrations import is_database_available
    from app.repositories.weather_repository import WeatherRepository

    if not is_database_available():
        return None, None
    try:
        from app.database import get_db

        db = next(get_db())
        return WeatherRepository(db), db
    except Exception:
        return None, None


class ReadingStorageHandler:
    """Stores readings from ReadingGenerated and publishes ReadingStored + WeatherUpdated.

    Preserves each reading's *original measurement timestamp* (not the DB
    insertion time) so historical analysis and baselines use the time the
    measurement was actually taken. Falls back to "now" only when the source
    did not supply a timestamp.

    Gracefully degrades when no database is available — events are still
    published so downstream handlers (alert engine, WebSocket) continue to work.
    """

    def __init__(self, db: Session, event_bus: EventBus) -> None:
        self._db = db
        self._event_bus = event_bus

    async def handle(self, event: ReadingGenerated) -> None:
        readings_data = event.readings

        raw_list = (
            readings_data
            if isinstance(readings_data, list)
            else readings_data.get("readings", [])
        )

        repo, session = _get_reading_repo()

        for rd in raw_list:
            # Use the source measurement timestamp, not the ingestion time.
            measured_at = _parse_timestamp(rd.get("timestamp")) or datetime.now(timezone.utc)

            await self._event_bus.publish(
                ReadingStored(
                    string_id=str(rd.get("string_id", "0")),
                    recorded_at=measured_at,
                    voltage=rd.get("voltage_v") or rd.get("voltage"),
                    current=rd.get("current_a") or rd.get("current"),
                    power=rd.get("power_w") or rd.get("power"),
                    irradiance=rd.get("irradiance_wpm2") or rd.get("irradiance"),
                    temperature=rd.get("temperature_c") or rd.get("temperature"),
                ),
            )

            if repo is not None and session is not None:
                try:
                    from app.models.telemetry.string_reading import StringReading
                    from app.providers.huawei.string_identity import coerce_string_id

                    string_id = coerce_string_id(session, rd.get("string_id", "0"))
                    reading = StringReading(
                        string_id=string_id,
                        recorded_at=measured_at,
                        voltage=rd.get("voltage_v") or rd.get("voltage"),
                        current=rd.get("current_a") or rd.get("current"),
                        power=rd.get("power_w") or rd.get("power"),
                        irradiance=rd.get("irradiance_wpm2") or rd.get("irradiance"),
                        temperature=rd.get("temperature_c") or rd.get("temperature"),
                    )
                    session.add(reading)
                    session.commit()
                except Exception:
                    session.rollback()
                    logger.warning("Could not persist readings to database")

        weather_data: dict[str, Any] | None = None
        if isinstance(readings_data, dict):
            weather_data = readings_data.get("weather") or event.weather
        if weather_data is None and hasattr(event, "weather"):
            weather_data = event.weather

        if weather_data is not None:
            w_repo, w_session = _get_weather_repo()
            if w_repo is not None and w_session is not None:
                try:
                    from app.models.telemetry.weather_reading import WeatherReading

                    w_measured_at = _parse_timestamp(weather_data.get("timestamp")) or datetime.now(timezone.utc)
                    record = WeatherReading(
                        recorded_at=w_measured_at,
                        temperature=weather_data.get("temperature_c"),
                        humidity=weather_data.get("humidity_pct"),
                        irradiance=weather_data.get("irradiance_wpm2"),
                        wind_speed=weather_data.get("wind_speed_mps"),
                        wind_direction=weather_data.get("wind_direction"),
                        precipitation=weather_data.get("precipitation_mm"),
                    )
                    w_session.add(record)
                    w_session.commit()
                except Exception:
                    w_session.rollback()
                    logger.warning("Could not persist weather to database")

            await self._event_bus.publish(
                WeatherUpdated(weather_data=weather_data),
            )


def _parse_timestamp(value: Any) -> datetime | None:
    """Parse an ISO timestamp from a provider reading; tolerate None."""
    if value is None:
        return None
    try:
        ts = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except (TypeError, ValueError):
        return None


class AlertProcessingHandler:
    """Processes ReadingStored events through the AlertEngine and publishes alerts."""

    def __init__(self, alert_engine: Any, event_bus: EventBus) -> None:
        self._alert_engine = alert_engine
        self._event_bus = event_bus

    async def handle(self, event: ReadingStored) -> None:
        alert_reading = AlertReading(
            string_id=event.string_id,
            timestamp=event.recorded_at,
            voltage=event.voltage,
            current=event.current,
            power=event.power,
            irradiance=event.irradiance,
            ambient_temperature=event.temperature,
        )

        try:
            alerts = self._alert_engine.process_reading(alert_reading)
        except Exception:
            logger.exception("Alert engine failed for reading %s", event.string_id)
            return

        for alert in alerts:
            severity_str = (
                alert.severity.value
                if hasattr(alert.severity, "value")
                else str(alert.severity)
            )
            await self._event_bus.publish(
                AlertCreated(
                    alert_id=alert.alert_id,
                    string_id=event.string_id,
                    alert_type=alert.alert_type,
                    severity=severity_str,
                    reason=alert.reason,
                    expected_value=alert.expected_value,
                    actual_value=alert.actual_value,
                    deviation_pct=alert.deviation_pct,
                    raw_alert=(
                        alert.model_dump()
                        if hasattr(alert, "model_dump")
                        else None
                    ),
                ),
            )


class AlertResolutionHandler:
    """Monitors readings and publishes AlertResolved when the engine auto-resolves."""

    def __init__(self, alert_engine: Any, event_bus: EventBus) -> None:
        self._alert_engine = alert_engine
        self._event_bus = event_bus

    async def handle(self, event: ReadingStored) -> None:
        try:
            active = self._alert_engine.get_active_alerts()
        except Exception:
            return
        for alert in list(active):
            status_val = (
                alert.status.value
                if hasattr(alert.status, "value")
                else str(alert.status)
            )
            if status_val == "resolved":
                await self._event_bus.publish(
                    AlertResolved(
                        alert_id=alert.alert_id,
                        string_id=event.string_id,
                        alert_type=alert.alert_type,
                    ),
                )


class WebSocketBroadcastHandler:
    """Bridges internal events to WebSocket clients."""

    def __init__(self, broadcaster: Broadcaster) -> None:
        self._broadcaster = broadcaster

    async def handle_alert_created(self, event: AlertCreated) -> None:
        payload = {
            "alert_id": event.alert_id,
            "string_id": event.string_id,
            "alert_type": event.alert_type,
            "severity": event.severity,
            "reason": event.reason,
            "expected_value": event.expected_value,
            "actual_value": event.actual_value,
            "deviation_pct": event.deviation_pct,
        }
        try:
            await self._broadcaster.broadcast_alert_created(payload)
        except Exception:
            logger.debug("WebSocket broadcast failed (no clients)")

    async def handle_alert_resolved(self, event: AlertResolved) -> None:
        payload = {
            "alert_id": event.alert_id,
            "string_id": event.string_id,
            "alert_type": event.alert_type,
        }
        try:
            await self._broadcaster.broadcast_alert_resolved(payload)
        except Exception:
            logger.debug("WebSocket broadcast failed (no clients)")

    async def handle_reading_generated(self, event: ReadingGenerated) -> None:
        data: dict[str, Any] = {"readings": event.readings}
        if event.weather:
            data["weather"] = event.weather
        try:
            await self._broadcaster.broadcast_new_reading(data)
        except Exception:
            logger.debug("WebSocket broadcast failed (no clients)")

    async def handle_weather_updated(self, event: WeatherUpdated) -> None:
        try:
            await self._broadcaster.broadcast_weather_update(event.weather_data)
        except Exception:
            logger.debug("WebSocket broadcast failed (no clients)")


class SchedulerTickHandler:
    """Handles SchedulerTick events for various tick types."""

    def __init__(
        self,
        provider: IDataProvider,
        event_bus: EventBus,
        broadcaster: Broadcaster | None = None,
    ) -> None:
        self._provider = provider
        self._event_bus = event_bus
        self._broadcaster = broadcaster

    async def handle(self, event: SchedulerTick) -> None:
        if event.tick_type == "simulator":
            await self._handle_simulator_tick()
        elif event.tick_type == "alert_processing":
            await self._handle_alert_processing()
        elif event.tick_type == "cleanup":
            await self._handle_cleanup()
        elif event.tick_type == "statistics_update":
            await self._handle_statistics_update()

    async def _handle_simulator_tick(self) -> None:
        try:
            readings = await self._provider.get_current_readings()
            weather = await self._provider.get_weather()

            reading_list: list[dict[str, Any]] = (
                readings
                if isinstance(readings, list)
                else readings.get("readings", [])
            )

            await self._event_bus.publish(
                ReadingGenerated(
                    readings=reading_list,
                    weather=weather,
                ),
            )
            logger.debug(
                "Published ReadingGenerated with %d readings",
                len(reading_list),
            )
        except Exception:
            logger.exception("Simulator tick failed")

    async def _handle_alert_processing(self) -> None:
        if self._broadcaster is not None:
            try:
                await self._broadcaster.broadcast_heartbeat_check()
            except Exception:
                logger.exception("Alert processing heartbeat failed")

    async def _handle_cleanup(self) -> None:
        if self._broadcaster is not None:
            try:
                await self._broadcaster.broadcast_heartbeat_check()
            except Exception:
                logger.exception("Cleanup heartbeat check failed")

    async def _handle_statistics_update(self) -> None:
        logger.info("Statistics update tick — no-op pending DB integration")
