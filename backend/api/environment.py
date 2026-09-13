from fastapi import APIRouter

router = APIRouter()


@router.get("/environment")
def get_environment():
    """Return environmental conditions for the voyage context.

    TODO: Replace with ingestion of weather, ocean, and sea-ice environmental products.
    """
    return {
        "environment": {
            "sea_ice": {
                "concentration": 0.63,
                "ice_edge_distance_km": 58.4,
                "risk_level": "moderate",
            },
            "weather": {
                "wind_speed_m_s": 11.7,
                "wind_direction_deg": 145,
                "temperature_c": -4.2,
                "pressure_hpa": 988.1,
                "precipitation_mm": 2.1,
            },
            "ocean": {
                "surface_current_u_m_s": 0.22,
                "surface_current_v_m_s": -0.15,
                "sea_surface_temperature_c": 1.3,
            },
        }
    }
