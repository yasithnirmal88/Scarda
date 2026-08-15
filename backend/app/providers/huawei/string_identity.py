"""Resolve Scarda composite string ids to integer string FKs.

Readings arrive from the provider with composite ids like ``SEC01-INV01-STR01``
(derived from the Huawei/mock ``inv-01-str-001``). The ``string_readings``
table stores an integer FK into ``strings.id``. This module resolves (and, on
first sight, lazily creates) the section → inverter → string hierarchy by code
so readings can be stored and historical queries can group by the same logical
string.

This keeps the provider abstraction intact: the rest of Scarda only ever sees
the composite id; the integer FK is an internal storage detail resolved here.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class ParsedScardaId:
    section_code: str   # e.g. "SEC01"
    inverter_code: str  # e.g. "INV01"
    string_code: str    # e.g. "STR01"
    section_name: str
    inverter_name: str
    string_name: str


def parse_scarda_string_id(string_id: str) -> ParsedScardaId | None:
    """Parse ``SEC01-INV01-STR01`` into its section/inverter/string parts.

    Returns ``None`` for ids that don't match the Scarda composite convention
    (callers then fall back to whatever integer id they already have).
    """
    parts = string_id.split("-")
    if len(parts) != 3:
        return None
    sec, inv, st = parts
    if not (sec.startswith("SEC") and inv.startswith("INV") and st.startswith("STR")):
        return None
    return ParsedScardaId(
        section_code=sec,
        inverter_code=inv,
        string_code=st,
        section_name=f"Section {sec[3:]}",
        inverter_name=f"Inverter {inv[3:]}",
        string_name=f"String {st[3:]}",
    )


def resolve_string_id(session: Session, string_id: str) -> int | None:
    """Return the integer ``strings.id`` for a composite Scarda string id.

    Looks up the section/inverter/string by code, creating any missing level on
    the fly so the plant hierarchy is populated from the live data source
    (exactly what happens when the real Huawei API is connected). Returns
    ``None`` only when the id is not a recognised composite id.
    """
    parsed = parse_scarda_string_id(string_id)
    if parsed is None:
        return None

    try:
        from app.models.master.inverter import Inverter
        from app.models.master.section import Section
        from app.models.master.string import String
        from app.repositories.inverter_repository import InverterRepository
        from app.repositories.section_repository import SectionRepository
        from app.repositories.string_repository import StringRepository

        sec_repo = SectionRepository(session)
        inv_repo = InverterRepository(session)
        str_repo = StringRepository(session)

        section = sec_repo.find_by_code(parsed.section_code)
        if section is None:
            section = Section(
                code=parsed.section_code,
                name=parsed.section_name,
                description=f"Auto-created from provider data ({parsed.section_code})",
            )
            section = sec_repo.create(section)

        inverter = inv_repo.find_by_code(parsed.inverter_code)
        if inverter is None:
            inverter = Inverter(
                code=parsed.inverter_code,
                section_id=section.id,
                name=parsed.inverter_name,
            )
            inverter = inv_repo.create(inverter)

        string = str_repo.find_by_code(parsed.string_code)
        if string is None:
            string = String(
                code=parsed.string_code,
                inverter_id=inverter.id,
                name=parsed.string_name,
            )
            string = str_repo.create(string)

        return string.id
    except Exception:
        logger.debug("Could not resolve string id %s", string_id, exc_info=True)
        return None


def coerce_string_id(session: Session | None, raw: Any) -> int:
    """Best-effort integer string id from any provider reading value.

    Composite Scarda ids are resolved (creating hierarchy if needed) when a
    session is available; numeric ids pass through; everything else yields 0
    (the legacy sentinel for "unknown string").
    """
    if raw is None:
        return 0
    raw_str = str(raw)
    try:
        return int(raw_str)
    except ValueError:
        pass
    if session is not None:
        resolved = resolve_string_id(session, raw_str)
        if resolved is not None:
            return resolved
    return 0
