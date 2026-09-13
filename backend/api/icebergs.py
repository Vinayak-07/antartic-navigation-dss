from fastapi import APIRouter

router = APIRouter()


@router.get("/icebergs")
def get_icebergs():
    """Return mock iceberg observations and risk summary.

    TODO: Replace with observed data ingestion and physics-based forecast outputs.
    """
    return {
        "icebergs": [
            {
                "id": "A-204",
                "lat": -50.4,
                "lon": 20.6,
                "drift_speed_m_s": 0.42,
                "risk_level": "high",
                "size_class": "large",
            },
            {
                "id": "A-185",
                "lat": -52.1,
                "lon": 21.8,
                "drift_speed_m_s": 0.31,
                "risk_level": "moderate",
                "size_class": "medium",
            },
        ],
        "summary": {
            "detected_count": 2,
            "high_risk_count": 1,
            "nearest_iceberg_id": "A-204",
        },
    }


@router.post("/icebergs/predict")
def predict_icebergs():
    """Return a mock trajectory prediction response.

    TODO: Replace with numerical integration from the physics model.
    """
    return {
        "trajectory": {
            "duration_hours": 48,
            "ensemble_size": 25,
            "uncertainty": 0.18,
        },
        "positions": [
            {"time_hours": 0, "lat": -50.4, "lon": 20.6},
            {"time_hours": 12, "lat": -50.9, "lon": 21.1},
            {"time_hours": 24, "lat": -51.4, "lon": 21.7},
            {"time_hours": 36, "lat": -51.8, "lon": 22.2},
            {"time_hours": 48, "lat": -52.2, "lon": 22.8},
        ],
    }
