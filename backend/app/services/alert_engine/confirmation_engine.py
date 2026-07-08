from __future__ import annotations

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from app.services.alert_engine.config import AlertEngineConfig
from app.services.alert_engine.types import Deviation, PendingEntry, RuleResult

logger = logging.getLogger(__name__)


class ConfirmationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CLEARED = "cleared"


class ConfirmationEngine:
    def __init__(self, config: AlertEngineConfig) -> None:
        self._config = config
        self._pending: dict[str, PendingEntry] = {}

    def record_reading(
        self, string_id: str, results: list[RuleResult], now: datetime
    ) -> ConfirmationStatus:
        if not results:
            return self._handle_recovery(string_id, now)

        primary = results[0]
        existing = self._pending.get(string_id)

        if existing is None:
            self._pending[string_id] = PendingEntry(
                string_id=string_id,
                rule_name=primary.rule_name,
                reason=primary.reason,
                severity=primary.severity,
                deviation=primary.deviation,
                first_seen=now,
                last_seen=now,
                count=1,
            )
            logger.info("Pending created for %s: %s", string_id, primary.reason)
            return ConfirmationStatus.PENDING

        if self._is_expired(existing, now):
            del self._pending[string_id]
            logger.info("Pending expired for %s", string_id)
            return ConfirmationStatus.CLEARED

        existing.count += 1
        existing.last_seen = now
        existing.reason = primary.reason
        existing.severity = primary.severity
        existing.deviation = primary.deviation

        if existing.count >= self._config.confirmation_cycles:
            del self._pending[string_id]
            logger.info("Alert confirmed for %s after %d cycles", string_id, existing.count)
            return ConfirmationStatus.CONFIRMED

        return ConfirmationStatus.PENDING

    def _handle_recovery(self, string_id: str, now: datetime) -> ConfirmationStatus:
        existing = self._pending.get(string_id)
        if existing is not None:
            del self._pending[string_id]
            logger.info("Pending cleared for %s — reading returned to normal", string_id)
            return ConfirmationStatus.CLEARED
        return ConfirmationStatus.CLEARED

    def _is_expired(self, entry: PendingEntry, now: datetime) -> bool:
        delay = timedelta(minutes=self._config.max_confirmation_delay_minutes)
        return (now - entry.first_seen) > delay

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    def clear_all(self) -> None:
        self._pending.clear()
