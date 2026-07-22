"""initial schema — generated from SQLAlchemy models

Revision ID: initial_schema
Revises:
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "initial_schema"
down_revision: str | None = None


def upgrade() -> None:
    # ── PostgreSQL ENUM types ──────────────────────────────────────
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'engineer', 'manager')")
    op.execute(
        "CREATE TYPE inverterstatus AS ENUM "
        "('online', 'offline', 'error', 'maintenance')"
    )
    op.execute("CREATE TYPE stringstatus AS ENUM ('active', 'inactive', 'error')")
    op.execute(
        "CREATE TYPE alertseverity AS ENUM ('info', 'warning', 'critical')"
    )
    op.execute(
        "CREATE TYPE alertstatus AS ENUM ('active', 'acknowledged', 'resolved')"
    )
    op.execute(
        "CREATE TYPE maintenancestatus AS ENUM "
        "('scheduled', 'in_progress', 'completed', 'cancelled')"
    )

    # ── users ──────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "admin", "engineer", "manager",
                name="userrole", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"])

    # ── sections ───────────────────────────────────────────────────
    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sections_id"), "sections", ["id"])

    # ── inverters ──────────────────────────────────────────────────
    op.create_table(
        "inverters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("model_number", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "online", "offline", "error", "maintenance",
                name="inverterstatus", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["section_id"], ["sections.id"],
            name=op.f("fk_inverters_section_id_sections"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inverters_id"), "inverters", ["id"])
    op.create_index(
        op.f("ix_inverters_section_id"), "inverters", ["section_id"],
    )

    # ── strings ────────────────────────────────────────────────────
    op.create_table(
        "strings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("inverter_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("panel_count", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active", "inactive", "error",
                name="stringstatus", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["inverter_id"], ["inverters.id"],
            name=op.f("fk_strings_inverter_id_inverters"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_strings_id"), "strings", ["id"])
    op.create_index(
        op.f("ix_strings_inverter_id"), "strings", ["inverter_id"],
    )

    # ── string_readings ────────────────────────────────────────────
    op.create_table(
        "string_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("string_id", sa.Integer(), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("voltage", sa.Float(), nullable=True),
        sa.Column("current", sa.Float(), nullable=True),
        sa.Column("power", sa.Float(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("irradiance", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["string_id"], ["strings.id"],
            name=op.f("fk_string_readings_string_id_strings"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_string_readings_id"), "string_readings", ["id"])
    op.create_index(
        op.f("ix_string_readings_string_id"),
        "string_readings", ["string_id"],
    )
    op.create_index(
        op.f("ix_string_readings_recorded_at"),
        "string_readings", ["recorded_at"],
    )

    # ── weather_readings ───────────────────────────────────────────
    op.create_table(
        "weather_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("irradiance", sa.Float(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("wind_direction", sa.String(length=10), nullable=True),
        sa.Column("precipitation", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_weather_readings_id"), "weather_readings", ["id"])
    op.create_index(
        op.f("ix_weather_readings_recorded_at"),
        "weather_readings", ["recorded_at"],
    )

    # ── baselines ──────────────────────────────────────────────────
    op.create_table(
        "baselines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("string_id", sa.Integer(), nullable=False),
        sa.Column("expected_power", sa.Float(), nullable=True),
        sa.Column("expected_voltage", sa.Float(), nullable=True),
        sa.Column("expected_current", sa.Float(), nullable=True),
        sa.Column("expected_energy", sa.Float(), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["string_id"], ["strings.id"],
            name=op.f("fk_baselines_string_id_strings"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_baselines_id"), "baselines", ["id"])
    op.create_index(
        op.f("ix_baselines_string_id"), "baselines", ["string_id"],
    )

    # ── alerts ─────────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("inverter_id", sa.Integer(), nullable=True),
        sa.Column("string_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column(
            "severity",
            postgresql.ENUM(
                "info", "warning", "critical",
                name="alertseverity", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active", "acknowledged", "resolved",
                name="alertstatus", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["inverter_id"], ["inverters.id"],
            name=op.f("fk_alerts_inverter_id_inverters"),
        ),
        sa.ForeignKeyConstraint(
            ["string_id"], ["strings.id"],
            name=op.f("fk_alerts_string_id_strings"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_id"), "alerts", ["id"])
    op.create_index(op.f("ix_alerts_status"), "alerts", ["status"])
    op.create_index(
        op.f("ix_alerts_created_at"), "alerts", ["created_at"],
    )

    # ── maintenance_logs ───────────────────────────────────────────
    op.create_table(
        "maintenance_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("inverter_id", sa.Integer(), nullable=True),
        sa.Column("string_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("scheduled_date", sa.DateTime(), nullable=True),
        sa.Column("completed_date", sa.DateTime(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "scheduled", "in_progress", "completed", "cancelled",
                name="maintenancestatus", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["inverter_id"], ["inverters.id"],
            name=op.f("fk_maintenance_logs_inverter_id_inverters"),
        ),
        sa.ForeignKeyConstraint(
            ["string_id"], ["strings.id"],
            name=op.f("fk_maintenance_logs_string_id_strings"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name=op.f("fk_maintenance_logs_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_logs_id"), "maintenance_logs", ["id"])
    op.create_index(
        op.f("ix_maintenance_logs_status"),
        "maintenance_logs", ["status"],
    )

    # ── system_settings ────────────────────────────────────────────
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(
        op.f("ix_system_settings_id"), "system_settings", ["id"],
    )


def downgrade() -> None:
    # ── Drop tables (reverse dependency order) ─────────────────────
    op.drop_table("system_settings")
    op.drop_table("maintenance_logs")
    op.drop_table("alerts")
    op.drop_table("baselines")
    op.drop_table("weather_readings")
    op.drop_table("string_readings")
    op.drop_table("strings")
    op.drop_table("inverters")
    op.drop_table("sections")
    op.drop_table("users")

    # ── Drop PostgreSQL ENUM types ─────────────────────────────────
    op.execute("DROP TYPE IF EXISTS maintenancestatus")
    op.execute("DROP TYPE IF EXISTS alertstatus")
    op.execute("DROP TYPE IF EXISTS alertseverity")
    op.execute("DROP TYPE IF EXISTS stringstatus")
    op.execute("DROP TYPE IF EXISTS inverterstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
