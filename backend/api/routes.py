from fastapi import APIRouter, Depends
from backend.simulation import TripEngine

router = APIRouter()

engine = TripEngine()

@router.post("/routes/optimize")
def optimize_routes(trip_id: str = None):
    """Adapter over canonical TripEngine — not mock."""
    if trip_id and trip_id in engine.trips:
        trip = engine.get_trip(trip_id)
        return {"routes": trip.get("routes", {}), "source": "trip_engine", "trip_id": trip_id}
    return {"status": "deprecated", "message": "Use /api/trips endpoint with trip_id; mock data no longer served.", "routes": {}}
