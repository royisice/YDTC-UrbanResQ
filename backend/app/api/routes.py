from fastapi import APIRouter, Query
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from backend.app.schemas import Location, Reading, Alert, Risk, TimeSeriesResponse

router = APIRouter()

# ---------- helper: severity logic ----------
def severity_from_flood(water_level_cm: float, rainfall_mm: float) -> str:
    # simple rules for prototype (easy to change later)
    if water_level_cm >= 60 or rainfall_mm >= 30:
        return "HIGH"
    if water_level_cm >= 40 or rainfall_mm >= 15:
        return "MEDIUM"
    return "LOW"

def severity_from_heat(temp_c: float, humidity: int) -> str:
    # simple heat risk proxy
    if temp_c >= 35 and humidity >= 70:
        return "HIGH"
    if temp_c >= 33:
        return "MEDIUM"
    return "LOW"

# ---------- endpoints ----------
@router.get("/locations", response_model=List[Location])
def get_locations():
    return [
        {"id": "loc_1", "name": "Bedok", "lat": 1.3236, "lon": 103.9273, "region": "East"},
        {"id": "loc_2", "name": "Jurong", "lat": 1.3327, "lon": 103.7436, "region": "West"},
    ]

@router.get("/readings/latest", response_model=Reading)
def get_latest_reading(location_id: str = Query(...)):
    now = datetime.now(timezone.utc)
    return {
        "location_id": location_id,
        "timestamp": now,
        "rainfall_mm": 12.4,
        "water_level_cm": 38.2,
        "temp_c": 33.1,
        "humidity": 78
    }

@router.get("/readings/timeseries", response_model=TimeSeriesResponse)
def get_readings_timeseries(
    location_id: str = Query(...),
    hours: int = Query(24, ge=1, le=168)  # last X hours (1 to 168)
):
    now = datetime.now(timezone.utc)
    points = []

    # Generate mock data points every 2 hours
    for i in range(0, hours + 1, 2):
        ts = now - timedelta(hours=(hours - i))
        points.append({
            "location_id": location_id,
            "timestamp": ts,
            "rainfall_mm": round(5 + (i % 6) * 2.1, 1),
            "water_level_cm": round(25 + (i % 8) * 4.3, 1),
            "temp_c": round(31 + (i % 5) * 0.8, 1),
            "humidity": 70 + (i % 10),
        })

    return {"location_id": location_id, "points": points}

@router.get("/risk/latest", response_model=Risk)
def get_latest_risk(location_id: str = Query(...)):
    # for now, compute risk from the mock latest reading logic
    now = datetime.now(timezone.utc)

    # you can later replace with real DB/AI output
    rainfall_mm = 12.4
    water_level_cm = 38.2
    temp_c = 33.1
    humidity = 78

    flood_sev = severity_from_flood(water_level_cm, rainfall_mm)
    heat_sev = severity_from_heat(temp_c, humidity)

    # map severity -> 0-100 style score (mock)
    sev_to_score = {"LOW": 25, "MEDIUM": 60, "HIGH": 85}
    flood_risk = sev_to_score[flood_sev]
    heat_risk = sev_to_score[heat_sev]

    # overall level (max of both)
    overall = "HIGH" if "HIGH" in (flood_sev, heat_sev) else ("MEDIUM" if "MEDIUM" in (flood_sev, heat_sev) else "LOW")

    return {
        "location_id": location_id,
        "timestamp": now,
        "flood_risk": flood_risk,
        "heat_risk": heat_risk,
        "risk_level": overall
    }

@router.get("/alerts", response_model=List[Alert])
def get_alerts(
    status: str = Query("open"),
    location_id: Optional[str] = None
):
    now = datetime.now(timezone.utc)

    # mock reading values (later come from DB/AI)
    rainfall_mm = 28.0
    water_level_cm = 62.0
    temp_c = 35.2
    humidity = 76

    flood_sev = severity_from_flood(water_level_cm, rainfall_mm)
    heat_sev = severity_from_heat(temp_c, humidity)

    alerts = [
        {
            "id": "alert_flood_1",
            "type": "FLOOD",
            "severity": flood_sev,
            "message": f"Flood risk {flood_sev}: water level {water_level_cm}cm, rainfall {rainfall_mm}mm.",
            "location_id": "loc_1",
            "timestamp": now,
            "status": status
        },
        {
            "id": "alert_heat_1",
            "type": "HEAT",
            "severity": heat_sev,
            "message": f"Heat risk {heat_sev}: temp {temp_c}°C, humidity {humidity}%.",
            "location_id": "loc_2",
            "timestamp": now,
            "status": status
        }
    ]

    if location_id:
        alerts = [a for a in alerts if a["location_id"] == location_id]

    return alerts
