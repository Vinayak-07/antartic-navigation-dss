from fastapi import APIRouter

router = APIRouter()


@router.post("/voyage/analyze")
def analyze_voyage():
    """Analyze a voyage request and return a decision-support payload.

    TODO: Replace with real voyage validation, data assembly, and model outputs.
    PLACEHOLDER: This stub returns a mock structure that matches the future API schema.
    """
    return {
        "voyage": {
            "voyage_id": "voyage-001",
            "vessel": "RV Aurora",
            "origin": "Cape Town",
            "destination": "Bharati Station",
            "departure_time": "2026-01-15T06:00:00Z",
            "forecast_horizon_days": 10,
            "status": "PLANNED",
        },
        "sea_ice": {
            "summary": "mock sea-ice forecast",
            "risk_level": "moderate",
            "confidence": 0.74,
        },
        "icebergs": {
            "detected_count": 3,
            "nearest_iceberg": {
                "id": "A-204",
                "distance_km": 142.5,
            },
        },
        "environment": {
            "weather": "stable",
            "ocean_current": "moderate southward",
        },
        "routes": {
            "recommended": {
                "name": "Recommended Route",
                "score": 81.3,
            },
            "alternatives": [
                {"name": "Shortest Route", "score": 72.2},
                {"name": "Low-Risk Route", "score": 88.6},
            ],
        },
    }
