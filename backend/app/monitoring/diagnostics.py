from __future__ import annotations

import logging
import os
import platform
import sys
from datetime import datetime, timezone
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


async def get_diagnostics(
    scheduler_startup: Any = None,
    provider: Any = None,
) -> dict[str, Any]:
    python_info = {
        "version": sys.version,
        "executable": sys.executable,
        "platform": sys.platform,
    }

    system_info = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "python": python_info,
        "cwd": os.getcwd(),
        "pid": os.getpid(),
    }

    app_info = {
        "name": settings.APP_NAME,
        "debug": settings.DEBUG,
        "scheduler_enabled": settings.scheduler.ENABLED,
        "database_url": settings.database.URL.split("@")[-1] if "@" in settings.database.URL else settings.database.URL,
    }

    scheduler_info: dict[str, Any] = {"status": "unavailable"}
    if scheduler_startup is not None:
        try:
            running = scheduler_startup.scheduler.is_running
            jobs = scheduler_startup.scheduler.get_jobs()
            scheduler_info = {
                "status": "running" if running else "stopped",
                "jobs": jobs,
            }
        except Exception as e:
            scheduler_info = {"status": "error", "message": str(e)}

    provider_info: dict[str, Any] = {"status": "unavailable"}
    if provider is not None:
        provider_info = {"status": "configured", "type": type(provider).__name__}

    return {
        "system": system_info,
        "application": app_info,
        "scheduler": scheduler_info,
        "provider": provider_info,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
