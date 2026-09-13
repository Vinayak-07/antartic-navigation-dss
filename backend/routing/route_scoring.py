"""Route cost and safety scoring."""

from backend.scientific import distance_km, risk_at


def score_route(route, sea_ice, icebergs, environment, simulation_hours, speed_kn: float = 11.5):
    distance = sum(distance_km(first, second) for first, second in zip(route, route[1:]))
    risks = [risk_at(point[0], point[1], simulation_hours, sea_ice, icebergs, environment) for point in route]
    sea_ice_risk = max(item["sea_ice_risk"] for item in risks)
    iceberg_risk = max(item["iceberg_risk"] for item in risks)
    weather_risk = max(item["weather_risk"] for item in risks)
    overall = max(item["overall_navigation_risk"] for item in risks)
    duration = distance / max(1.0, speed_kn * 1.852)
    fuel = distance * (0.044 + 0.018 * overall)
    score = distance + 8.0 * duration + 0.8 * fuel + 700.0 * (0.42 * sea_ice_risk + 0.38 * iceberg_risk + 0.20 * weather_risk)
    return {"distance_km": round(distance, 2), "estimated_duration_hours": round(duration, 2), "travel_time_hours": round(duration, 2), "fuel_tonnes": round(fuel, 2), "safety_score": round(1.0 - overall, 4), "risk_score": round(overall, 4), "sea_ice_risk": round(sea_ice_risk, 4), "iceberg_risk": round(iceberg_risk, 4), "weather_risk": round(weather_risk, 4), "cost": round(score, 2), "reasons": ["Balances distance, fuel, weather, sea ice, and iceberg exposure"]}
