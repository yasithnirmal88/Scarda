"""convert string_readings into a TimescaleDB hypertable

Revision ID: convert_hypertable
Revises: add_code_columns
Create Date: 2026-07-09

TimescaleDB requires the partitioning column (recorded_at) to be part of
any unique / primary key constraint on the hypertable. The existing
`string_readings` table has a surrogate `id` primary key only, so we need
to widen that constraint to (id, recorded_at) before calling
create_hypertable().
"""

from collections.abc import Sequence

from alembic import op

revision: str = "convert_hypertable"
down_revision: str | None = "add_code_columns"


def upgrade() -> None:
    # ── Enable TimescaleDB (safe if already enabled) ──────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    # ── Widen the primary key to include recorded_at ──────────────────
    op.execute("ALTER TABLE string_readings DROP CONSTRAINT string_readings_pkey")
    op.execute(
        "ALTER TABLE string_readings ADD CONSTRAINT string_readings_pkey "
        "PRIMARY KEY (id, recorded_at)"
    )

    # ── Convert to hypertable, partitioned by recorded_at ─────────────
    op.execute(
        "SELECT create_hypertable("
        "'string_readings', 'recorded_at', "
        "if_not_exists => TRUE, migrate_data => TRUE)"
    )

    # ── Helpful index for per-string time-range queries ───────────────
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_string_readings_string_time "
        "ON string_readings (string_id, recorded_at DESC)"
    )

    # ── Compression: readings older than 7 days ───────────────────────
    op.execute(
        "ALTER TABLE string_readings SET ("
        "timescaledb.compress, "
        "timescaledb.compress_segmentby = 'string_id')"
    )
    op.execute(
        "SELECT add_compression_policy('string_readings', INTERVAL '7 days', "
        "if_not_exists => TRUE)"
    )

    # ── Continuous aggregate: hourly rollups for dashboards ───────────
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS string_readings_hourly
        WITH (timescaledb.continuous) AS
        SELECT
            string_id,
            time_bucket('1 hour', recorded_at) AS bucket,
            AVG(current) AS avg_current,
            AVG(voltage) AS avg_voltage,
            AVG(power) AS avg_power,
            AVG(temperature) AS avg_temperature,
            AVG(irradiance) AS avg_irradiance,
            MIN(power) AS min_power,
            MAX(power) AS max_power
        FROM string_readings
        GROUP BY string_id, bucket
        WITH NO DATA
        """
    )
    op.execute(
        "SELECT add_continuous_aggregate_policy('string_readings_hourly', "
        "start_offset => INTERVAL '3 hours', "
        "end_offset => INTERVAL '10 minutes', "
        "schedule_interval => INTERVAL '30 minutes', "
        "if_not_exists => TRUE)"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS string_readings_hourly")
    op.execute(
        "SELECT remove_compression_policy('string_readings', if_exists => TRUE)"
    )
    op.execute("DROP INDEX IF EXISTS idx_string_readings_string_time")

    # Note: Timescale doesn't support converting a hypertable back to a
    # plain table in-place. Downgrading fully requires recreating the
    # table. This downgrade only reverts the compression/aggregate layer.
