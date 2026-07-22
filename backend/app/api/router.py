from fastapi import APIRouter

from app.api.endpoints import (
    alerts,
    auth,
    dashboard,
    inverters,
    maintenance,
    monitoring,
    readings,
    reports,
    sections,
    settings,
    strings,
    users,
    weather,
)
from app.websocket import router as websocket_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(sections.router, prefix="/sections", tags=["Sections"])
api_router.include_router(inverters.router, prefix="/inverters", tags=["Inverters"])
api_router.include_router(strings.router, prefix="/strings", tags=["Strings"])
api_router.include_router(readings.router, prefix="/readings", tags=["Readings"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(websocket_router, tags=["WebSocket"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
