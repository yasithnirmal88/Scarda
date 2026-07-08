from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class String(Base):
    __tablename__ = "strings"

    id = Column(Integer, primary_key=True, index=True)
    inverter_id = Column(Integer, ForeignKey("inverters.id"), nullable=False)
    name = Column(String(100), nullable=False)
    panel_count = Column(Integer, default=0)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    inverter = relationship("Inverter", back_populates="strings")
    readings = relationship("StringReading", back_populates="string")
    baselines = relationship("Baseline", back_populates="string")
