from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.simulation import TripEngine

router = APIRouter()
engine = TripEngine()


class TripCreateRequest(BaseModel):
    vessel: str = "RV Aurora"
    origin: str = "Cape Town"
    destination: str = "Bharati Station"
    departure_time: Optional[str] = None
    scenario: str = "NORMAL"
    seed: Optional[int] = None


class TripSpeedRequest(BaseModel):
    speed: float = 1.0


class TripStepRequest(BaseModel):
    steps: int = 1


class TripSeekRequest(BaseModel):
    target_time: float = 0.0


@router.post("/trips")
def create_trip(payload: TripCreateRequest):
    trip = engine.create_trip(
        vessel=payload.vessel,
        origin=payload.origin,
        destination=payload.destination,
        scenario=payload.scenario,
        departure_time=payload.departure_time,
        seed=payload.seed,
    )
    return trip


@router.get("/trips")
def list_trips():
    return {"trips": engine.list_trips()}


@router.get("/trips/{trip_id}")
def get_trip(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.get_trip(trip_id)


@router.post("/trips/{trip_id}/start")
def start_trip(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.start_trip(trip_id)


@router.post("/trips/{trip_id}/pause")
def pause_trip(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.pause_trip(trip_id)


@router.post("/trips/{trip_id}/reset")
def reset_trip(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.reset_trip(trip_id)


@router.post("/trips/{trip_id}/step")
def step_trip(trip_id: str, payload: TripStepRequest):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.step_trip(trip_id, steps=payload.steps)


@router.post("/trips/{trip_id}/seek")
def seek_trip(trip_id: str, payload: TripSeekRequest):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.seek_trip(trip_id, payload.target_time)


@router.post("/trips/{trip_id}/speed")
def set_speed(trip_id: str, payload: TripSpeedRequest):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.set_speed(trip_id, payload.speed)


@router.get("/trips/{trip_id}/state")
def get_state(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.get_trip_state(trip_id)


@router.get("/trips/{trip_id}/timeline")
def get_timeline(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"timeline": engine.get_trip_timeline(trip_id)}


@router.get("/trips/{trip_id}/events")
def get_events(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"events": engine.get_trip_events(trip_id)}


@router.post("/trips/{trip_id}/branch")
def create_branch(trip_id: str):
    if trip_id not in engine.trips:
        raise HTTPException(status_code=404, detail="Trip not found")
    return engine.create_trip_from_point(trip_id, engine.trips[trip_id]["current_simulation_time"])
