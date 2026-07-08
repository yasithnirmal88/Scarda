from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(Integer, primary_key=True, index=True)
    string_id = Column(Integer, ForeignKey("strings.id"), nullable=False)
    expected_power = Column(Float, nullable=True)
    expected_voltage = Column(Float, nullable=True)
    expected_current = Column(Float, nullable=True)
    expected_energy = Column(Float, nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    string = relationship("String", back_populates="baselines")
