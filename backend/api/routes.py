from fastapi import APIRouter

router = APIRouter()


@router.post("/routes/optimize")
def optimize_routes():
    """Return mock route optimization results.

    TODO: Replace with route graph search or cost-grid implementation.
    """
    return {
        "routes": {
            "shortest": {
                "name": "Shortest Route",
                "distance_km": 1845.2,
                "travel_time_hours": 92.1,
                "fuel_tonnes": 86.5,
                "risk_score": 0.74,
            },
            "recommended": {
                "name": "Recommended Route",
                "distance_km": 1912.8,
                "travel_time_hours": 95.7,
                "fuel_tonnes": 89.4,
                "risk_score": 0.43,
                "explanation": [
                    "Avoids high sea-ice concentration",
                    "Avoids predicted iceberg corridor",
                    "Reduces environmental risk",
                    "Acceptable additional distance",
                ],
            },
            "low_risk": {
                "name": "Low-Risk Alternative",
                "distance_km": 2015.6,
                "travel_time_hours": 101.9,
                "fuel_tonnes": 93.1,
                "risk_score": 0.29,
            },
        },
        "comparison": {
            "route_1": "Shortest",
            "route_2": "Recommended",
            "route_3": "Low-risk alternative",
        },
    }
