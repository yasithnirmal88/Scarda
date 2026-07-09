from fastapi import APIRouter, Request

from app.monitoring.health import get_health
from app.monitoring.metrics import get_system_metrics
from app.monitoring.diagnostics import get_diagnostics

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    scheduler = getattr(request.app.state, "scheduler_startup", None)
    provider = getattr(request.app.state, "provider", None)
    return await get_health(scheduler, provider)


@router.get("/metrics")
async def metrics():
    return await get_system_metrics()


@router.get("/diagnostics")
async def diagnostics(request: Request):
    scheduler = getattr(request.app.state, "scheduler_startup", None)
    provider = getattr(request.app.state, "provider", None)
    return await get_diagnostics(scheduler, provider)
