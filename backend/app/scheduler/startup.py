"""Scheduler initialization and job registration.

Creates and configures the background scheduler with all registered jobs
from the application configuration.
"""

from __future__ import annotations

import logging
from typing import Any

from app.scheduler.jobs import (
    alert_processing_job,
    cleanup_job,
    simulator_job,
    statistics_update_job,
)
from app.scheduler.scheduler import SchedulerService

logger = logging.getLogger(__name__)


class SchedulerStartup:
    def __init__(
        self,
        config: dict[str, Any],
        shared_context: dict[str, Any] | None = None,
    ) -> None:
        self._config = config
        self._shared_context = shared_context or {}
        self._scheduler = SchedulerService(config)

    def register_jobs(self) -> None:
        if not self._config.get("enabled", True):
            logger.info("Scheduler is disabled by configuration")
            return

        job_defs = [
            {
                "id": "simulator",
                "func": simulator_job,
                "trigger": "interval",
                "minutes": self._config.get("simulator_interval_minutes", 10),
            },
            {
                "id": "alert_processing",
                "func": alert_processing_job,
                "trigger": "interval",
                "minutes": self._config.get("alert_interval_minutes", 10),
            },
            {
                "id": "cleanup",
                "func": cleanup_job,
                "trigger": "interval",
                "hours": self._config.get("cleanup_interval_hours", 24),
            },
            {
                "id": "statistics_update",
                "func": statistics_update_job,
                "trigger": "interval",
                "minutes": self._config.get("stats_interval_minutes", 15),
            },
        ]

        for job_cfg in job_defs:
            func = job_cfg["func"]
            job_id = job_cfg["id"]
            trigger = job_cfg["trigger"]
            # Build remaining trigger args, excluding func/id/trigger
            trigger_args = {
                k: v for k, v in job_cfg.items()
                if k not in ("func", "id", "trigger")
            }
            self._scheduler.register_job(
                func, trigger, kwargs={"context": self._shared_context}, id=job_id, **trigger_args,
            )
            logger.info("Registered job: %s", job_id)

    def start(self) -> None:
        self.register_jobs()
        self._scheduler.start()

    def shutdown(self) -> None:
        self._scheduler.shutdown()

    @property
    def scheduler(self) -> SchedulerService:
        return self._scheduler
