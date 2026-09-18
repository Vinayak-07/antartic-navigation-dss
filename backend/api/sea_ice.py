from fastapi import APIRouter
from backend.simulation import TripEngine

router = APIRouter()
engine = TripEngine()

@router.get("/sea-ice")
def get_sea_ice(trip_id: str = None):
    """Adapter over canonical trip engine — synthetic data labelled."""
    if trip_id and trip_id in engine.trips:
        trip = engine.get_trip(trip_id)
        sea_ice = trip.get("sea_ice", {})
        sea_ice["data_mode"] = "SYNTHETIC DEMONSTRATION"
        sea_ice["data_source"] = "synthetic-sea-ice-1"
        return sea_ice
    return {"status": "deprecated", "message": "Provide trip_id or use /api/trips; synthetic demonstration data.", "data_mode": "SYNTHETIC DEMONSTRATION"}
