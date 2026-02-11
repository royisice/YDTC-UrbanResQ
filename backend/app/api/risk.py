from fastapi import APIRouter, Query
from datetime import datetime, timezone

router = APIRouter(prefix="/risk", tags=["Risk"])

@router.get("/latest")
def get_latest_risk(location_id: str = Query(...)):
    return {
        "location_id": location_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "flood_risk": 72,
        "heat_risk": 65,
        "risk_level": "HIGH"
    }
