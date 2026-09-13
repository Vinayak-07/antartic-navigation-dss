from typing import Optional

from pydantic import BaseModel, Field


class VoyageRequest(BaseModel):
    """Request payload for a voyage analysis.

    TODO: Expand with vessel, origin, destination, departure time, and route choice metadata.
    """

    vessel: str = Field(..., description="Selected vessel name")
    origin: str = Field(..., description="Voyage origin")
    destination: str = Field(..., description="Voyage destination")
    departure_time: str = Field(..., description="Departure time in ISO format")
    forecast_horizon_days: int = Field(default=10, ge=1, le=30)
    route_mode: Optional[str] = Field(default="recommended", description="Recommended route strategy")


class VoyageResponse(BaseModel):
    """Structured response returned to the frontend.

    TODO: Align with the final real model output schema.
    """

    voyage: dict
    sea_ice: dict
    icebergs: dict
    environment: dict
    routes: dict
