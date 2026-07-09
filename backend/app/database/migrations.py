from __future__ import annotations

import logging
from typing import Any

from alembic import command
from alembic.config import Config as AlembicConfig

from app.database.base import Base
from app.database.engine import engine
from app.models import (  # noqa: F401
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
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def run_alembic_migrations(alembic_ini_path: str = "alembic.ini") -> bool:
    try:
        alembic_cfg = AlembicConfig(alembic_ini_path)
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations applied successfully")
        return True
    except Exception:
        logger.exception("Alembic migration failed")
        return False


def create_migration_revision(message: str, alembic_ini_path: str = "alembic.ini") -> bool:
    try:
        alembic_cfg = AlembicConfig(alembic_ini_path)
        command.revision(alembic_cfg, autogenerate=True, message=message)
        logger.info("Migration revision created: %s", message)
        return True
    except Exception:
        logger.exception("Failed to create migration revision")
        return False
