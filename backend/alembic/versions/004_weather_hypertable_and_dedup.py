"""weather_readings hypertable + deduplication constraints

Revision ID: weather_hypertable_dedup
Revises: convert_hypertable
Create Date: 2026-08-15

Two things:

1. Convert ``weather_readings`` into a TimescaleDB hypertable partitioned by
   ``recorded_at``, mirroring what migration 003 did for ``string_readings``.
   The table already exists (initial_schema); this only reshapes it. No new
   historical table is created.

2. Add unique constraints so the historical backfill is idempotent: re-running
   a 90-day backfill must not duplicate rows. TimescaleDB requires the
   partitioning column (``recorded_at``) to be part of every unique constraint
   on a hypertable, which both constraints below satisfy.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "weather_hypertable_dedup"
down_revision: str | None = "convert_hypertable"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    # ── string_readings: dedup on (string_id, recorded_at) ────────────
    # Prevents a repeated 90-day backfill from inserting duplicate
    # (string, timestamp) rows. Includes recorded_at (the partition col) so
    # TimescaleDB permits it on the hypertable.
    #
    # TimescaleDB cannot add a unique constraint to a *compressed* hypertable,
    # and migration 003 already enabled compression. Turn compression off,
    # decompress any existing chunks, add the constraint, then re-enable
    # compression. On a fresh database there are no chunks to decompress.
    op.execute(
        "SELECT remove_compression_policy('string_readings', if_exists => TRUE)"
    )
    op.execute("ALTER TABLE string_readings SET (timescaledb.compress = false)")
    # decompress any existing chunks (no-op when the hypertable is empty).
    # show_chunks() returns regclass; decompress_chunk(regclass, boolean).
    op.execute(
        "SELECT decompress_chunk(c, true) FROM show_chunks('string_readings') c"
    )
    op.execute(
        "ALTER TABLE string_readings "
        "ADD CONSTRAINT uq_string_readings_string_recorded "
        "UNIQUE (string_id, recorded_at)"
    )
    op.execute(
        "ALTER TABLE string_readings SET (timescaledb.compress, "
        "timescaledb.compress_segmentby = 'string_id')"
    )
    op.execute(
        "SELECT add_compression_policy('string_readings', INTERVAL '7 days', "
        "if_not_exists => TRUE)"
    )

    # ── weather_readings: widen PK to include recorded_at, then hypertable ─
    op.execute(
        "ALTER TABLE weather_readings DROP CONSTRAINT weather_readings_pkey"
    )
    op.execute(
        "ALTER TABLE weather_readings ADD CONSTRAINT weather_readings_pkey "
        "PRIMARY KEY (id, recorded_at)"
    )
    op.execute(
        "ALTER TABLE weather_readings "
        "ADD CONSTRAINT uq_weather_readings_recorded "
        "UNIQUE (recorded_at)"
    )
    op.execute(
        "SELECT create_hypertable("
        "'weather_readings', 'recorded_at', "
        "if_not_exists => TRUE, migrate_data => TRUE)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_weather_readings_time "
        "ON weather_readings (recorded_at DESC)"
    )
    # Compression for weather older than 7 days.
    op.execute(
        "ALTER TABLE weather_readings SET (timescaledb.compress)"
    )
    op.execute(
        "SELECT add_compression_policy('weather_readings', INTERVAL '7 days', "
        "if_not_exists => TRUE)"
    )


def downgrade() -> None:
    op.execute(
        "SELECT remove_compression_policy('weather_readings', if_exists => TRUE)"
    )
    op.execute("DROP INDEX IF EXISTS idx_weather_readings_time")
    op.execute(
        "ALTER TABLE weather_readings "
        "DROP CONSTRAINT IF EXISTS uq_weather_readings_recorded"
    )
    op.execute("ALTER TABLE weather_readings DROP CONSTRAINT weather_readings_pkey")
    op.execute(
        "ALTER TABLE weather_readings ADD CONSTRAINT weather_readings_pkey "
        "PRIMARY KEY (id)"
    )
    op.execute(
        "ALTER TABLE string_readings "
        "DROP CONSTRAINT IF EXISTS uq_string_readings_string_recorded"
    )
