from typing import List

from pydantic import BaseModel, Field


class RouteSummary(BaseModel):
    """Summary of a candidate route."""

    name: str
    distance_km: float
    travel_time_hours: float
    fuel_tonnes: float
    risk_score: float = Field(ge=0.0, le=1.0)
    explanation: List[str] = []


class RouteComparison(BaseModel):
    """Comparison structure for short, recommended, and low-risk routes."""

    route_1: str
    route_2: str
    route_3: str
