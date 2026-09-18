"""Dynamic route cost grid."""

from backend.scientific import distance_km, risk_at, iceberg_route_risk
from backend.utils.coordinates import DEFAULT_ANTARCTIC_MASK
from backend.routing.constraints import apply_constraints


def build_cost_grid(origin, destination, sea_ice, icebergs, environment, simulation_hours, step: float = 2.0, iceberg_trajectories: dict = None, vessel_ice_class: str = "PC6"):
    """
    Build a cost grid for routing that accounts for future iceberg trajectories.
    
    Args:
        iceberg_trajectories: Optional dict mapping iceberg_id to trajectory data
                             for evaluating future positions at forecast horizons.
        vessel_ice_class: Vessel polar class for ice capability constraints
    """
    latitude_min = min(origin[0], destination[0]) - 10.0
    latitude_max = max(origin[0], destination[0]) + 10.0
    longitude_min = min(origin[1], destination[1]) - 16.0
    longitude_max = max(origin[1], destination[1]) + 16.0
    cells = {}
    latitude = latitude_min
    while latitude <= latitude_max:
        longitude = longitude_min
        while longitude <= longitude_max:
            # Base risk at current simulation time
            risk = risk_at(latitude, longitude, simulation_hours, sea_ice, icebergs, environment)
            
            # Add future iceberg risk by evaluating trajectories at forecast horizons
            # This ensures the route optimizer "sees" where icebergs will be
            if iceberg_trajectories:
                for iceberg in icebergs:
                    iceberg_id = iceberg.get("id")
                    if iceberg_id and iceberg_id in iceberg_trajectories:
                        trajectory = iceberg_trajectories[iceberg_id]
                        # Evaluate route risk using the iceberg's future trajectory
                        # We create a minimal route segment (the cell itself) to check proximity
                        cell_route = [[latitude, longitude], [latitude, longitude]]
                        future_risk = iceberg_route_risk(iceberg, cell_route, trajectory)
                        # Add future risk to the cell's iceberg risk
                        risk["iceberg_risk"] = max(risk["iceberg_risk"], future_risk["risk_score"])
                        risk["overall_navigation_risk"] = max(risk["overall_navigation_risk"], future_risk["risk_score"])
            
            blocked = risk["sea_ice_risk"] > 0.92 or risk["iceberg_risk"] > 0.88
            cells[(round(latitude, 4), round(longitude, 4))] = {"risk": risk, "blocked": blocked, "cost": 0.0 if blocked else 1.0 + 5.0 * risk["overall_navigation_risk"]}
            longitude += step
        latitude += step
    
    grid = {"cells": cells, "step": step, "bounds": (latitude_min, latitude_max, longitude_min, longitude_max), "origin": tuple(origin), "destination": tuple(destination)}
    
    # Apply routing constraints (land/coast blocking, ice capability)
    grid = apply_constraints(grid, vessel_ice_class=vessel_ice_class, coast_buffer_km=10.0, step=step)
    
    return grid
