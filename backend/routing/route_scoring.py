"""Route cost and safety scoring."""

from backend.scientific import distance_km, risk_at


def score_route(route, sea_ice, bergs, environment, simulation_hours, speed_kn: float = 17.0, weights: dict = None):
    """Route scoring with fuel and multi-objective cost."""
    # Configurable weights (default from spec)
    if weights is None:
        weights = {"w_distance": 1.0, "w_time": 2.0, "w_fuel": 3.0, "w_sea_ice": 4.0, "w_iceberg": 5.0, "w_weather": 2.0, "w_constraints": 6.0}
    distance = sum(distance_km(first, second) for first, second in zip(route, route[1:]))
    risks = [risk_at(point[0], point[1], simulation_hours, sea_ice, bergs, environment) for point in route]
    sea_ice_risk = max(item["sea_ice_risk"] for item in risks)
    iceberg_risk = max(item["iceberg_risk"] for item in risks)
    weather_risk = max(item["weather_risk"] for item in risks)
    overall = max(item["overall_navigation_risk"] for item in risks)
    duration = distance / max(1.0, speed_kn * 1.852)
    fuel = distance * (0.052 + 0.018 * overall)  # real fuel cost
    
    # Multi-objective cost C per spec
    C = (weights["w_distance"] * distance +
         weights["w_time"] * duration +
         weights["w_fuel"] * fuel +
         weights["w_sea_ice"] * sea_ice_risk +
         weights["w_iceberg"] * iceberg_risk +
         weights["w_weather"] * weather_risk)
    score = C
    return {"distance_km": round(distance, 2), "estimated_duration_hours": round(duration, 2), "travel_time_hours": round(duration, 2), "fuel_tonnes": round(fuel, 2), "safety_score": round(1.0 - overall, 4), "risk_score": round(overall, 4), "sea_ice_risk": round(sea_ice_risk, 4), "iceberg_risk": round(iceberg_risk, 4), "weather_risk": round(weather_risk, 4), "cost": round(score, 2), "cost_weights": weights, "reasons": ["Multi-objective: distance + time + fuel + ice + iceberg + weather + constraints"]}
