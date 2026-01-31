from fastapi import APIRouter, Query
from datetime import datetime, timezone

router = APIRouter()

@router.get("/locations")
def get_locations():
    return [
        {"id": "loc_1", "name": "Bedok", "lat": 1.3236, "lon": 103.9273, "region": "East"},
        {"id": "loc_2", "name": "Jurong", "lat": 1.3327, "lon": 103.7436, "region": "West"},
    ]

@router.get("/readings/latest")
def get_latest_reading(location_id: str = Query(...)):
    now = datetime.now(timezone.utc).isoformat()
    return {
        "location_id": location_id,
        "timestamp": now,
        "rainfall_mm": 12.4,
        "water_level_cm": 38.2,
        "temp_c": 33.1,
        "humidity": 78
    }

@router.get("/alerts")
def get_alerts(status: str = Query("open")):
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "id": "alert_1",
            "type": "FLOOD",
            "severity": "HIGH",
            "message": "Water level rising rapidly.",
            "location_id": "loc_1",
            "timestamp": now,
            "status": status
        }
    ]
