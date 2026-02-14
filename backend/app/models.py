from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from .db import Base

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    location_id = Column(String, index=True)

    timestamp = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))

    rainfall_mm = Column(Float, default=0.0)
    water_level_cm = Column(Float, default=0.0)
    temp_c = Column(Float, default=0.0)
    humidity = Column(Integer, default=0)
    salinity = Column(Float, default=0.0)

    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String)
    severity = Column(String)
    message = Column(String)
    location_id = Column(String, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="open")
