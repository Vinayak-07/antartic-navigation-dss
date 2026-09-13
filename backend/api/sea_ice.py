from fastapi import APIRouter

router = APIRouter()


@router.get("/sea-ice")
def get_sea_ice():
    """Return mock sea-ice forecast information.

    TODO: Later replace with real dataset-driven outputs.
    """
    return {
        "forecast": {
            "grid": "antarctic-sector-grid",
            "forecast_horizon_days": 10,
            "concentration_mean": 0.63,
            "risk_level": "moderate",
            "confidence": 0.74,
            "uncertainty": 0.12,
        },
        "records": [
            {
                "lat": -61.2,
                "lon": 27.8,
                "concentration": 0.71,
                "risk_score": 0.66,
            },
            {
                "lat": -62.5,
                "lon": 28.3,
                "concentration": 0.55,
                "risk_score": 0.48,
            },
        ],
    }
