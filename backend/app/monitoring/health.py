"""Health check logic for the application.

Provides async functions to check database connectivity, scheduler status,
and data provider health. All checks are non-blocking.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from app.database.engine import engine

logger = logging.getLogger(__name__)


def _blocking_db_check() -> None:
    """Execute a synchronous database health check (SELECT 1)."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


async def check_database() -> dict[str, Any]:
    """Check database connectivity without blocking the event loop."""
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _blocking_db_check)
        return {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        logger.warning("Database health check failed: %s", e)
        return {"status": "unhealthy", "message": str(e)}


async def check_scheduler(scheduler_startup: Any = None) -> dict[str, Any]:
    """Check scheduler status via public API (no private attribute access)."""
    if scheduler_startup is None:
        return {"status": "unavailable", "message": "Scheduler not initialized"}
    try:
        running = scheduler_startup.scheduler.is_running
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
    """Check data provider health."""
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
    """Aggregate health checks for all application components."""
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
