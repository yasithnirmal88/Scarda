from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base
from app.utils.enums import InverterStatus


class Inverter(Base):
    __tablename__ = "inverters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("sections.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[InverterStatus] = mapped_column(
        Enum(InverterStatus), nullable=False, default=InverterStatus.OFFLINE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    section = relationship("Section", back_populates="inverters")
    strings = relationship("String", back_populates="inverter", cascade="all, delete-orphan")
