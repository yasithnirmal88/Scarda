import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.migrations import init_database
from app.middleware.auth import AuthMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.scheduler.startup import SchedulerStartup

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggerMiddleware)

app.include_router(api_router, prefix="/api")

_scheduler_startup: SchedulerStartup | None = None


@app.on_event("startup")
async def on_startup() -> None:
    global _scheduler_startup
    setup_logging()
    logger.info("Starting %s", settings.APP_NAME)
    init_database()

    scheduler_config = {
        "enabled": settings.SCHEDULER_ENABLED,
        "simulator_interval_minutes": settings.SCHEDULER_SIMULATOR_INTERVAL_MINUTES,
        "alert_interval_minutes": settings.SCHEDULER_ALERT_INTERVAL_MINUTES,
        "cleanup_interval_hours": settings.SCHEDULER_CLEANUP_INTERVAL_HOURS,
        "stats_interval_minutes": settings.SCHEDULER_STATS_INTERVAL_MINUTES,
    }
    _scheduler_startup = SchedulerStartup(scheduler_config)
    _scheduler_startup.start()
    app.state.scheduler_startup = _scheduler_startup
    from app.providers import create_provider
    app.state.provider = create_provider()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if _scheduler_startup is not None:
        _scheduler_startup.shutdown()


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": "0.1.0", "status": "running"}


@app.get("/api/scheduler/jobs")
async def get_scheduler_jobs():
    if _scheduler_startup is None:
        return []
    return _scheduler_startup.scheduler.get_jobs()


@app.post("/api/scheduler/jobs/{job_id}/pause")
async def pause_scheduler_job(job_id: str):
    if _scheduler_startup is None:
        return {"ok": False}
    ok = _scheduler_startup.scheduler.pause_job(job_id)
    return {"ok": ok}


@app.post("/api/scheduler/jobs/{job_id}/resume")
async def resume_scheduler_job(job_id: str):
    if _scheduler_startup is None:
        return {"ok": False}
    ok = _scheduler_startup.scheduler.resume_job(job_id)
    return {"ok": ok}


@app.post("/api/scheduler/jobs/{job_id}/stop")
async def stop_scheduler_job(job_id: str):
    if _scheduler_startup is None:
        return {"ok": False}
    ok = _scheduler_startup.scheduler.stop_job(job_id)
    return {"ok": ok}
