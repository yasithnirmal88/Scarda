"""add code columns to sections, inverters, strings

Revision ID: add_code_columns
Revises: initial_schema
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "add_code_columns"
down_revision: str | None = "initial_schema"


def upgrade() -> None:
    # ── sections.code ────────────────────────────────────────────────
    op.add_column("sections", sa.Column("code", sa.String(length=50), nullable=True))
    op.execute("UPDATE sections SET code = 'Section-' || id WHERE code IS NULL")
    op.alter_column("sections", "code", nullable=False)
    op.create_unique_constraint(op.f("uq_sections_code"), "sections", ["code"])

    # ── inverters.code ───────────────────────────────────────────────
    op.add_column("inverters", sa.Column("code", sa.String(length=50), nullable=True))
    op.execute(
        "UPDATE inverters SET code = 'INV-' || lpad(id::text, 2, '0') "
        "WHERE code IS NULL"
    )
    op.alter_column("inverters", "code", nullable=False)
    op.create_unique_constraint(op.f("uq_inverters_code"), "inverters", ["code"])

    # ── strings.code ─────────────────────────────────────────────────
    # STR-<inverter_id>-<string_id_within_inverter>
    op.add_column("strings", sa.Column("code", sa.String(length=50), nullable=True))
    op.execute(
        """
        UPDATE strings s
        SET code = 'STR-' || lpad(s.inverter_id::text, 2, '0') || '-' ||
                    lpad(s.id::text, 2, '0')
        WHERE code IS NULL
        """
    )
    op.alter_column("strings", "code", nullable=False)
    op.create_unique_constraint(op.f("uq_strings_code"), "strings", ["code"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_strings_code"), "strings", type_="unique")
    op.drop_column("strings", "code")

    op.drop_constraint(op.f("uq_inverters_code"), "inverters", type_="unique")
    op.drop_column("inverters", "code")

    op.drop_constraint(op.f("uq_sections_code"), "sections", type_="unique")
    op.drop_column("sections", "code")
