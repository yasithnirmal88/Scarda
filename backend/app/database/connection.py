from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    driver: str = "postgresql+psycopg2"
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "solar_aim"
    use_timescaledb: bool = False

    @property
    def url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def url_with_timescaledb(self) -> str:
        base = self.url
        if self.use_timescaledb:
            return f"{base}?options=-c%20timescaledb.telemetry_level=off"
        return base


def build_database_url(
    driver: str = "postgresql+psycopg2",
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    password: str = "postgres",
    database: str = "solar_aim",
    use_timescaledb: bool = False,
) -> str:
    cfg = DatabaseConfig(
        driver=driver,
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        use_timescaledb=use_timescaledb,
    )
    return cfg.url_with_timescaledb


def is_timescaledb_url(url: str) -> bool:
    return "timescaledb" in url.lower()


def parse_database_url(url: str) -> DatabaseConfig:
    parts = url.split("://", 1)
    driver = parts[0] if len(parts) == 2 else "postgresql+psycopg2"
    remaining = parts[1] if len(parts) == 2 else url
    user_pass, host_port_db = remaining.split("@", 1)
    user, password = user_pass.split(":", 1)
    host_port, database = host_port_db.split("/", 1)
    host = host_port
    port = 5432
    if ":" in host_port:
        host, port_str = host_port.split(":", 1)
        port = int(port_str)
    database = database.split("?")[0]
    return DatabaseConfig(
        driver=driver,
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        use_timescaledb=is_timescaledb_url(url),
    )
