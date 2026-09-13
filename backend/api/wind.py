"""HTTP boundary for the external numerical-weather wind visualization field."""

from fastapi import APIRouter, HTTPException, Query

from backend.wind import DEFAULT_BOUNDS, DEFAULT_SPACING_DEG, WindFieldService, WindGridRequest, WindProviderError


router = APIRouter()
service = WindFieldService()


@router.get("/wind")
def get_wind(
    south: float = Query(DEFAULT_BOUNDS["south"]),
    north: float = Query(DEFAULT_BOUNDS["north"]),
    west: float = Query(DEFAULT_BOUNDS["west"]),
    east: float = Query(DEFAULT_BOUNDS["east"]),
    spacing: float = Query(DEFAULT_SPACING_DEG),
    refresh: bool = Query(False),
):
    """Return one cached, normalized U/V field for the Leaflet velocity layer."""
    try:
        return service.get_field(WindGridRequest(south=south, north=north, west=west, east=east, spacing=spacing), refresh=refresh)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except WindProviderError as exc:
        raise HTTPException(status_code=503, detail=f"Wind data unavailable: {exc}") from exc
