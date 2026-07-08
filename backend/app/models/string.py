from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base
from app.utils.enums import StringStatus


class String(Base):
    __tablename__ = "strings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inverter_id: Mapped[int] = mapped_column(Integer, ForeignKey("inverters.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    panel_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[StringStatus] = mapped_column(
        Enum(StringStatus), nullable=False, default=StringStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    inverter = relationship("Inverter", back_populates="strings")
    readings = relationship("StringReading", back_populates="string", cascade="all, delete-orphan")
    baselines = relationship("Baseline", back_populates="string", cascade="all, delete-orphan")
