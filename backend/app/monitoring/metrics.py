from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


async def get_memory_usage() -> dict[str, Any]:
    try:
        import psutil

        mem = psutil.virtual_memory()
        return {
            "total_bytes": mem.total,
            "available_bytes": mem.available,
            "used_bytes": mem.used,
            "percent_used": mem.percent,
        }
    except ImportError:
        logger.debug("psutil not available, returning limited memory info")
        return {
            "total_bytes": None,
            "available_bytes": None,
            "used_bytes": None,
            "percent_used": None,
            "note": "Install psutil for full memory metrics",
        }


async def get_cpu_usage() -> dict[str, Any]:
    try:
        import psutil

        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count_logical": os.cpu_count() or 0,
            "count_physical": psutil.cpu_count(logical=False) or 0,
        }
    except ImportError:
        logger.debug("psutil not available, returning limited CPU info")
        return {
            "percent": None,
            "count_logical": os.cpu_count() or 0,
            "count_physical": None,
            "note": "Install psutil for full CPU metrics",
        }


async def get_system_metrics() -> dict[str, Any]:
    memory = await get_memory_usage()
    cpu = await get_cpu_usage()

    return {
        "memory": memory,
        "cpu": cpu,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
