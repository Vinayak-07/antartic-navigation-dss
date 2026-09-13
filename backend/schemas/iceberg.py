from typing import List, Optional

from pydantic import BaseModel, Field


class IcebergObservation(BaseModel):
    """Observed iceberg metadata."""

    id: str
    lat: float
    lon: float
    size_class: str
    risk_level: str
    mass_t: Optional[float] = None
    draft_m: Optional[float] = None
    freeboard_m: Optional[float] = None


class IcebergTrajectory(BaseModel):
    """Trajectory output placeholder schema."""

    duration_hours: int
    ensemble_size: int
    uncertainty: float = Field(ge=0.0, le=1.0)
    positions: List[dict]
