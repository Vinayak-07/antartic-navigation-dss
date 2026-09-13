from typing import List

from pydantic import BaseModel, Field


class SeaIceCell(BaseModel):
    """A single sea-ice grid cell."""

    lat: float
    lon: float
    concentration: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    forecast_horizon_days: int = Field(ge=1)
    confidence: float = Field(ge=0.0, le=1.0)


class SeaIceForecast(BaseModel):
    """Mock schema for sea-ice forecast response."""

    grid: str
    forecast_horizon_days: int
    concentration_mean: float
    risk_level: str
    confidence: float
    uncertainty: float
    records: List[SeaIceCell]
