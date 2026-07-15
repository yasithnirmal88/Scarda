from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from app.services.alert_engine.types import AlertData
from app.utils.enums import AlertState

logger = logging.getLogger(__name__)


class BaseAlertRepository(ABC):
    @abstractmethod
    def create(self, alert: AlertData) -> AlertData:
        ...

    @abstractmethod
    def get_active(self) -> list[AlertData]:
        ...

    @abstractmethod
    def get_history(self, limit: int = 100) -> list[AlertData]:
        ...

    @abstractmethod
    def acknowledge(self, alert_id: str) -> AlertData | None:
        ...

    @abstractmethod
    def resolve(self, alert_id: str) -> AlertData | None:
        ...

    @abstractmethod
    def find_active_by_string_and_type(self, string_id: str, alert_type: str) -> AlertData | None:
        ...

    @abstractmethod
    def find_pending_by_string_and_type(self, string_id: str, alert_type: str) -> AlertData | None:
        ...


class InMemoryAlertRepository(BaseAlertRepository):
    def __init__(self) -> None:
        self._alerts: dict[str, AlertData] = {}

    def create(self, alert: AlertData) -> AlertData:
        self._alerts[alert.alert_id] = alert
        logger.info("Alert created: %s — %s", alert.alert_id, alert.reason)
        return alert

    def get_active(self) -> list[AlertData]:
        return [
            a for a in self._alerts.values()
            if a.status in (AlertState.ACTIVE, AlertState.ACKNOWLEDGED, AlertState.PENDING)
        ]

    def get_history(self, limit: int = 100) -> list[AlertData]:
        sorted_alerts = sorted(
            self._alerts.values(),
            key=lambda a: a.timestamp,
            reverse=True,
        )
        return sorted_alerts[:limit]

    def acknowledge(self, alert_id: str) -> AlertData | None:
        alert = self._alerts.get(alert_id)
        if alert is None:
            return None
        alert.status = AlertState.ACKNOWLEDGED
        alert.acknowledged = True
        return alert

    def resolve(self, alert_id: str) -> AlertData | None:
        alert = self._alerts.get(alert_id)
        if alert is None:
            return None
        alert.status = AlertState.RESOLVED
        alert.resolved = True
        alert.resolved_at = datetime.now()
        if alert.resolved_at is not None:
            alert.duration_seconds = (alert.resolved_at - alert.timestamp).total_seconds()
        return alert

    def find_active_by_string_and_type(self, string_id: str, alert_type: str) -> AlertData | None:
        for alert in self._alerts.values():
            if alert.string == string_id and alert.alert_type == alert_type:
                if alert.status in (AlertState.ACTIVE, AlertState.ACKNOWLEDGED):
                    return alert
        return None

    def find_pending_by_string_and_type(self, string_id: str, alert_type: str) -> AlertData | None:
        for alert in self._alerts.values():
            if alert.string == string_id and alert.alert_type == alert_type:
                if alert.status == AlertState.PENDING:
                    return alert
        return None
