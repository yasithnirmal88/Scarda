from __future__ import annotations

import logging

from alembic import command
from alembic.config import Config as AlembicConfig
from alembic.util.exc import CommandError

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

_CREATED: bool = False


def is_database_available() -> bool:
    """Return True once the database schema has been initialized successfully.

    Handlers use this to skip persistence attempts when PostgreSQL is
    unavailable so the app can run without blocking on dead connections.
    """
    return _CREATED


def init_database() -> None:
    global _CREATED
    if _CREATED:
        return

    logger.info("Initializing database schema...")

    success = run_alembic_migrations()
    if success:
        _CREATED = True
        logger.info("Alembic migrations applied successfully")
        return

    logger.warning(
        "Alembic migration failed — falling back to "
        "Base.metadata.create_all(). "
        "For production use 'alembic upgrade head'.",
    )
    try:
        Base.metadata.create_all(bind=engine)
        _CREATED = True
        logger.info("Database tables created via metadata.create_all()")
    except Exception as exc:
        logger.warning(
            "Could not create database tables: %s. "
            "The application will run without persistence. "
            "Start PostgreSQL and set DATABASE_URL to enable persistence.",
            exc,
        )


def run_alembic_migrations(alembic_ini_path: str = "alembic.ini") -> bool:
    try:
        alembic_cfg = AlembicConfig(alembic_ini_path)
        command.upgrade(alembic_cfg, "head")
        return True
    except CommandError:
        logger.warning("No migrations to apply or Alembic not yet configured")
        return False
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
