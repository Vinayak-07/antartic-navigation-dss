from fastapi import APIRouter
from backend.simulation import TripEngine

router = APIRouter()
engine = TripEngine()

@router.get("/voyage")
def get_voyage(trip_id: str = None):
    """Light adapter over canonical trip engine."""
    if trip_id and trip_id in engine.trips:
        return {"trip": engine.get_trip(trip_id), "source": "trip_engine"}
    return {"status": "deprecated", "message": "Provide trip_id.", "trip": None}
