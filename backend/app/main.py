import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.core.logging import setup_logging
from app.database.migrations import init_database
from app.events import (
    AlertProcessingHandler,
    AlertResolutionHandler,
    EventBus,
    ReadingStorageHandler,
    SchedulerTickHandler,
    WebSocketBroadcastHandler,
)
from app.middleware.auth import AuthMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.scheduler.startup import SchedulerStartup
from app.services.alert_engine.alert_engine import AlertEngine
from app.services.demo_mode import run_demo_once

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

_manager: Any | None = None
_broadcaster: Any | None = None
_event_bus: EventBus | None = None


def get_websocket_app() -> tuple[Any, Any]:
    global _manager, _broadcaster
    if _manager is None:
        from app.websocket.manager import ClientManager
        from app.websocket.broadcaster import Broadcaster

        _manager = ClientManager(heartbeat_interval=30)
        _broadcaster = Broadcaster(_manager)
    return _manager, _broadcaster


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def _get_db():
    from app.database import get_db
    try:
        return next(get_db())
    except Exception:
        return None


@app.on_event("startup")
async def on_startup() -> None:
    global _scheduler_startup
    setup_logging()
    logger.info("Starting %s", settings.APP_NAME)

    init_database()
    logger.info("Database initialized")

    sch = settings.scheduler
    scheduler_config = {
        "enabled": sch.ENABLED,
        "simulator_interval_minutes": sch.SIMULATOR_INTERVAL_MINUTES,
        "alert_interval_minutes": sch.ALERT_INTERVAL_MINUTES,
        "cleanup_interval_hours": sch.CLEANUP_INTERVAL_HOURS,
        "stats_interval_minutes": sch.STATS_INTERVAL_MINUTES,
    }

    event_bus = get_event_bus()

    from app.providers import create_provider

    provider = create_provider()
    app.state.provider = provider
    logger.info("Provider created: %s", type(provider).__name__)

    manager, broadcaster = get_websocket_app()
    app.state.websocket_manager = manager
    app.state.websocket_broadcaster = broadcaster
    logger.info("WebSocket manager and broadcaster initialized")

    alert_engine = AlertEngine()
    app.state.alert_engine = alert_engine
    logger.info("AlertEngine initialized")

    db = _get_db()

    reading_storage = ReadingStorageHandler(db, event_bus)
    alert_processing = AlertProcessingHandler(alert_engine, event_bus)
    alert_resolution = AlertResolutionHandler(alert_engine, event_bus)
    ws_handler = WebSocketBroadcastHandler(broadcaster)
    scheduler_handler = SchedulerTickHandler(provider, event_bus, broadcaster)

    event_bus.subscribe("reading.generated", reading_storage.handle)
    event_bus.subscribe("reading.generated", ws_handler.handle_reading_generated)
    event_bus.subscribe("reading.stored", alert_processing.handle)
    event_bus.subscribe("reading.stored", alert_resolution.handle)
    event_bus.subscribe("alert.created", ws_handler.handle_alert_created)
    event_bus.subscribe("alert.resolved", ws_handler.handle_alert_resolved)
    event_bus.subscribe("weather.updated", ws_handler.handle_weather_updated)
    event_bus.subscribe("scheduler.tick", scheduler_handler.handle)

    app.state.event_bus = event_bus
    logger.info(
        "EventBus initialized with %d subscribers",
        event_bus.subscriber_count(),
    )

    _scheduler_startup = SchedulerStartup(
        scheduler_config,
        shared_context={
            "event_bus": event_bus,
            "broadcaster": broadcaster,
            "provider": provider,
            "app": app,
        },
    )

    await run_demo_once(provider, event_bus)
    logger.info("Demo mode historical data generated")

    _scheduler_startup.start()
    app.state.scheduler_startup = _scheduler_startup
    logger.info("Scheduler started — entering live mode")


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
