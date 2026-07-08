import logging

from app.database.base import Base
from app.database.session import engine
from app.models import (  # noqa: F401 – registers models with Base
    Alert,
    Baseline,
    Inverter,
    MaintenanceLog,
    Section,
    String,
    StringReading,
    SystemSetting,
    User,
    WeatherReading,
)

logger = logging.getLogger(__name__)


def init_database() -> None:
    """Create all database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
