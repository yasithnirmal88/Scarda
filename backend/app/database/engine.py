from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings

logger = logging.getLogger(__name__)


def build_engine(
    database_url: str | None = None,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    echo: bool = False,
    use_null_pool: bool = False,
) -> Engine:
    url = database_url or settings.database.URL
    poolclass = NullPool if use_null_pool else QueuePool

    # psycopg2 blocks forever by default if PostgreSQL is down; give the app
    # a short window so it can fall back to running without persistence.
    connect_args: dict[str, Any] = {}
    if url.startswith("postgresql"):
        connect_args["connect_timeout"] = 3

    engine = create_engine(
        url,
        pool_pre_ping=pool_pre_ping,
        pool_size=pool_size if not use_null_pool else None,
        max_overflow=max_overflow if not use_null_pool else None,
        poolclass=poolclass,
        connect_args=connect_args,
        echo=echo,
    )

    _configure_engine(engine, url)
    return engine


def _configure_engine(engine: Engine, url: str) -> None:
    if "timescaledb" in url.lower():
        @event.listens_for(engine, "connect")
        def _set_timescaledb(dbapi_connection: Any, connection_record: Any) -> None:
            try:
                cursor = dbapi_connection.cursor()
                cursor.execute("SET timescaledb.telemetry_level=off")
                cursor.close()
            except Exception:
                pass

    logger.info("Engine created for %s", url.split("@")[-1] if "@" in url else url)


engine: Engine = build_engine()


def dispose_engine() -> None:
    engine.dispose()
    logger.info("Engine disposed")
