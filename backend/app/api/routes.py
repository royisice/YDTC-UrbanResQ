from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from .risk import router as risk_router
from app.deps import get_db
from app.models import Reading, Alert

router = APIRouter()
router.include_router(risk_router)


@router.get("/locations")
def get_locations():
    return [
        {"id": "loc_1", "name": "Bedok", "lat": 1.3236, "lon": 103.9273, "region": "East"},
        {"id": "loc_2", "name": "Jurong", "lat": 1.3327, "lon": 103.7436, "region": "West"},
    ]


@router.get("/ingest")
def ingest(
    deviceid: str = Query(...),
    location_id: str = Query("loc_1"),
    distance: float = Query(..., description="Water level (cm)"),
    Suhu: float = Query(..., description="Temperature C"),
    Latitude: float = Query(None),
    Longitude: float = Query(None),
    salinity: float = Query(0.0),
    humidity: int = Query(0),
    rainfall_mm: float = Query(0.0),
    db: Session = Depends(get_db),
):
    r = Reading(
        device_id=deviceid,
        location_id=location_id,
        timestamp=datetime.now(timezone.utc),
        water_level_cm=distance,
        temp_c=Suhu,
        lat=Latitude,
        lon=Longitude,
        salinity=salinity,
        humidity=humidity,
        rainfall_mm=rainfall_mm,
    )
    db.add(r)
    db.commit()
    db.refresh(r)

    return {"status": "ok", "saved_reading_id": r.id}


@router.get("/readings/latest")
def get_latest_reading(location_id: str = Query(...), db: Session = Depends(get_db)):
    row = (
        db.query(Reading)
        .filter(Reading.location_id == location_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )

    if not row:
        # fallback mock (so dashboard never breaks)
        now = datetime.now(timezone.utc).isoformat()
        return {
            "location_id": location_id,
            "timestamp": now,
            "rainfall_mm": 12.4,
            "water_level_cm": 38.2,
            "temp_c": 33.1,
            "humidity": 78,
            "salinity": 0.0,
            "lat": None,
            "lon": None,
            "device_id": None,
        }

    return {
        "location_id": row.location_id,
        "timestamp": row.timestamp.isoformat(),
        "rainfall_mm": row.rainfall_mm,
        "water_level_cm": row.water_level_cm,
        "temp_c": row.temp_c,
        "humidity": row.humidity,
        "salinity": row.salinity,
        "lat": row.lat,
        "lon": row.lon,
        "device_id": row.device_id,
    }


# ✅ NEW: history endpoint (for charts + table)
@router.get("/readings/history")
def get_readings_history(
    location_id: str = Query(...),
    limit: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Reading)
        .filter(Reading.location_id == location_id)
        .order_by(Reading.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "location_id": r.location_id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "rainfall_mm": r.rainfall_mm,
            "water_level_cm": r.water_level_cm,
            "temp_c": r.temp_c,
            "humidity": r.humidity,
            "salinity": r.salinity,
            "lat": r.lat,
            "lon": r.lon,
            "device_id": r.device_id,
        }
        for r in rows
    ]


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
