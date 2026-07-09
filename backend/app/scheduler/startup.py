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
    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._scheduler = SchedulerService(config)

    def register_jobs(self) -> None:
        if not self._config.get("enabled", True):
            logger.info("Scheduler is disabled by configuration")
            return

        jobs_config = [
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

        for job_cfg in jobs_config:
            func = job_cfg.pop("func")
            job_id = job_cfg["id"]
            trigger = job_cfg.pop("trigger")
            self._scheduler.register_job(func, trigger, **job_cfg)
            logger.info("Registered job: %s", job_id)

    def start(self) -> None:
        self.register_jobs()
        self._scheduler.start()

    def shutdown(self) -> None:
        self._scheduler.shutdown()

    @property
    def scheduler(self) -> SchedulerService:
        return self._scheduler
