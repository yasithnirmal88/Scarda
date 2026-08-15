from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base
from app.utils.enums import MaintenanceStatus, enum_values


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inverter_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("inverters.id"), nullable=True)
    string_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("strings.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[MaintenanceStatus] = mapped_column(
        Enum(MaintenanceStatus, values_callable=enum_values),
        nullable=False,
        default=MaintenanceStatus.SCHEDULED,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="maintenance_logs")
