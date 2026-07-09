from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from app.database.engine import engine

logger = logging.getLogger(__name__)


async def check_database() -> dict[str, Any]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        logger.warning("Database health check failed: %s", e)
        return {"status": "unhealthy", "message": str(e)}


async def check_scheduler(scheduler_startup: Any = None) -> dict[str, Any]:
    if scheduler_startup is None:
        return {"status": "unavailable", "message": "Scheduler not initialized"}
    try:
        running = scheduler_startup.scheduler._scheduler.running
        jobs = scheduler_startup.scheduler.get_jobs()
        return {
            "status": "healthy" if running else "stopped",
            "message": "Scheduler is running" if running else "Scheduler is stopped",
            "jobs": jobs,
        }
    except Exception as e:
        logger.warning("Scheduler health check failed: %s", e)
        return {"status": "unhealthy", "message": str(e)}


async def check_provider(provider: Any = None) -> dict[str, Any]:
    if provider is None:
        return {"status": "unavailable", "message": "No data provider configured"}
    try:
        result = await provider.health_check()
        return {"status": "healthy", "data": result}
    except Exception as e:
        logger.warning("Provider health check failed: %s", e)
        return {"status": "unhealthy", "message": str(e)}


async def get_health(
    scheduler_startup: Any = None,
    provider: Any = None,
) -> dict[str, Any]:
    db = await check_database()
    scheduler = await check_scheduler(scheduler_startup)
    provider_status = await check_provider(provider)

    all_healthy = all(
        c.get("status") == "healthy"
        for c in [db, scheduler, provider_status]
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "components": {
            "database": db,
            "scheduler": scheduler,
            "provider": provider_status,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
