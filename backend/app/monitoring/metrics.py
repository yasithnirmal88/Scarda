"""System metrics collection for monitoring endpoints.

Provides async-safe functions for memory and CPU usage that do not block
the FastAPI event loop.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Seed the cpu_percent counter on first call (returns 0.0 on first call
# when interval=None). Subsequent non-blocking calls return meaningful data.
_PSUTIL_CPU_SEEDED = False


def _blocking_cpu_percent() -> float:
    """Non-blocking CPU percent read. Uses interval=None for instant return."""
    import psutil
    return psutil.cpu_percent(interval=None)


async def get_memory_usage() -> dict[str, Any]:
    """Return memory usage metrics. Non-blocking."""
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
    """Return CPU usage metrics without blocking the event loop."""
    try:
        import psutil

        loop = asyncio.get_running_loop()
        percent = await loop.run_in_executor(None, _blocking_cpu_percent)
        return {
            "percent": percent,
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
    """Aggregate memory and CPU metrics."""
    memory = await get_memory_usage()
    cpu = await get_cpu_usage()

    return {
        "memory": memory,
        "cpu": cpu,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
