from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.deps import get_db
from app.models import Reading

router = APIRouter(prefix="/risk", tags=["Risk"])


def clamp(x: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, x))


@router.get("/latest")
def get_latest_risk(
    location_id: str = Query(..., description="Location ID e.g. loc_1"),
    db: Session = Depends(get_db),
):
    # 1) pull latest reading for this location
    r = (
        db.query(Reading)
        .filter(Reading.location_id == location_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )

    if not r:
        raise HTTPException(status_code=404, detail=f"No readings found for {location_id}")

    # 2) compute risk scores (simple rule-based, good enough for prototype)
    reasons = []

    # Flood score from water level (tune these thresholds as you like)
    # 0cm -> 0, 30cm -> 40, 60cm -> 80, 90cm+ -> 100
    flood_score = clamp((r.water_level_cm / 90.0) * 100.0)
    if r.water_level_cm >= 60:
        reasons.append("High water level")
    elif r.water_level_cm >= 30:
        reasons.append("Water level rising")

    # Heat score from temperature
    # 26C -> low, 35C -> high, 40C+ -> 100
    heat_score = clamp(((r.temp_c - 26.0) / 14.0) * 100.0)
    if r.temp_c >= 35:
        reasons.append("Extreme heat")
    elif r.temp_c >= 32:
        reasons.append("High temperature")

    # Salinity adds a bit (optional but matches your sensor requirement)
    salinity_score = clamp((r.salinity / 10.0) * 100.0)  # assume 0-10 typical
    if r.salinity >= 5:
        reasons.append("High salinity")

    # Weighted overall
    overall = clamp(0.5 * flood_score + 0.4 * heat_score + 0.1 * salinity_score)

    if overall >= 75:
        level = "HIGH"
    elif overall >= 45:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "location_id": location_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "flood_risk": round(flood_score, 1),
        "heat_risk": round(heat_score, 1),
        "salinity_risk": round(salinity_score, 1),
        "risk_score": round(overall, 1),
        "risk_level": level,
        "reasons": reasons if reasons else ["Normal conditions"],
        "latest_reading_id": r.id,
    }
