"""Dynamic route cost grid."""

from backend.scientific import distance_km, risk_at


def build_cost_grid(origin, destination, sea_ice, icebergs, environment, simulation_hours, step: float = 2.0):
    latitude_min = min(origin[0], destination[0]) - 10.0
    latitude_max = max(origin[0], destination[0]) + 10.0
    longitude_min = min(origin[1], destination[1]) - 16.0
    longitude_max = max(origin[1], destination[1]) + 16.0
    cells = {}
    latitude = latitude_min
    while latitude <= latitude_max:
        longitude = longitude_min
        while longitude <= longitude_max:
            risk = risk_at(latitude, longitude, simulation_hours, sea_ice, icebergs, environment)
            blocked = risk["sea_ice_risk"] > 0.92 or risk["iceberg_risk"] > 0.88
            cells[(round(latitude, 4), round(longitude, 4))] = {"risk": risk, "blocked": blocked, "cost": 0.0 if blocked else 1.0 + 5.0 * risk["overall_navigation_risk"]}
            longitude += step
        latitude += step
    return {"cells": cells, "step": step, "bounds": (latitude_min, latitude_max, longitude_min, longitude_max), "origin": tuple(origin), "destination": tuple(destination)}
