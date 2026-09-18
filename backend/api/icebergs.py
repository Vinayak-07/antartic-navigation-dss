from fastapi import APIRouter
from backend.simulation import TripEngine

router = APIRouter()
engine = TripEngine()

@router.get("/icebergs")
def get_icebergs(trip_id: str = None):
    """Adapter — synthetic iceberg observation set labelled."""
    if trip_id and trip_id in engine.trips:
        trip = engine.get_trip(trip_id)
        states = trip.get("iceberg_states", [])
        trajectories = trip.get("iceberg_trajectories", [])
        return {"iceberg_states": states, "iceberg_trajectories": trajectories, "data_mode": "SYNTHETIC DEMONSTRATION", "trip_id": trip_id}
    return {"status": "deprecated", "message": "Use /api/trips endpoint; synthetic iceberg demo.", "data_mode": "SYNTHETIC DEMONSTRATION"}
