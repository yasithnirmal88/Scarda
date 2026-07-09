from __future__ import annotations

import logging
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._scheduler = AsyncIOScheduler()
        self._config = config or {}

    def register_job(
        self,
        func: Any,
        trigger: str,
        **trigger_args: Any,
    ) -> Job | None:
        job_id = trigger_args.pop("id", None)
        try:
            job = self._scheduler.add_job(
                func,
                trigger,
                id=job_id,
                replace_existing=True,
                **trigger_args,
            )
            logger.info("Job registered: %s (trigger=%s)", job_id or func.__name__, trigger)
            return job
        except Exception:
            logger.exception("Failed to register job: %s", job_id or func.__name__)
            return None

    def pause_job(self, job_id: str) -> bool:
        try:
            self._scheduler.pause_job(job_id)
            logger.info("Job paused: %s", job_id)
            return True
        except Exception:
            logger.warning("Job not found for pause: %s", job_id)
            return False

    def resume_job(self, job_id: str) -> bool:
        try:
            self._scheduler.resume_job(job_id)
            logger.info("Job resumed: %s", job_id)
            return True
        except Exception:
            logger.warning("Job not found for resume: %s", job_id)
            return False

    def stop_job(self, job_id: str) -> bool:
        try:
            self._scheduler.remove_job(job_id)
            logger.info("Job stopped and removed: %s", job_id)
            return True
        except Exception:
            logger.warning("Job not found for removal: %s", job_id)
            return False

    def get_jobs(self) -> list[dict[str, Any]]:
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in self._scheduler.get_jobs()
        ]

    def start(self) -> None:
        if self._scheduler.running:
            logger.warning("Scheduler already running")
            return
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self, wait: bool = True) -> None:
        if not self._scheduler.running:
            return
        self._scheduler.shutdown(wait=wait)
        logger.info("Scheduler shut down")
