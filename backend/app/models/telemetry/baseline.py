from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Baseline(Base):
    __tablename__ = "baselines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    string_id: Mapped[int] = mapped_column(Integer, ForeignKey("strings.id"), nullable=False)
    expected_power: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_voltage: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_current: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    string = relationship("String", back_populates="baselines")
