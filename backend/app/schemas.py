from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    region: str

class Reading(BaseModel):
    location_id: str
    timestamp: datetime
    rainfall_mm: float
    water_level_cm: float
    temp_c: float
    humidity: int

class Alert(BaseModel):
    id: str
    type: str               # "FLOOD" | "HEAT"
    severity: str           # "LOW" | "MEDIUM" | "HIGH"
    message: str
    location_id: str
    timestamp: datetime
    status: str             # "open" | "closed"

class Risk(BaseModel):
    location_id: str
    timestamp: datetime
    flood_risk: int         # 0-100
    heat_risk: int          # 0-100
    risk_level: str         # "LOW" | "MEDIUM" | "HIGH"

class TimeSeriesResponse(BaseModel):
    location_id: str
    points: List[Reading]
