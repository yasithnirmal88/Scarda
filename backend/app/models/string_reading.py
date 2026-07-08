from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class StringReading(Base):
    __tablename__ = "string_readings"

    id = Column(Integer, primary_key=True, index=True)
    string_id = Column(Integer, ForeignKey("strings.id"), nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    voltage = Column(Float, nullable=True)
    current = Column(Float, nullable=True)
    power = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    irradiance = Column(Float, nullable=True)

    string = relationship("String", back_populates="readings")
