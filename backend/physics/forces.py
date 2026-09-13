"""Vector force balance for the iceberg state [x, y, u, v]."""

import math
from typing import Callable, Mapping

from backend.physics.coriolis import coriolis_parameter

AIR_DENSITY_KG_M3 = 1.225
WATER_DENSITY_KG_M3 = 1027.0
AIR_DRAG_COEFFICIENT = 0.9
WATER_DRAG_COEFFICIENT = 1.1
DEFAULT_ADDED_MASS_FACTOR = 1.15


def _vector_speed(u: float, v: float) -> float:
    return math.hypot(u, v)


def force_diagnostics(
    time_seconds: float,
    state,
    latitude: float,
    environment_provider: Callable,
    height_m: float,
    projected_area_m2: float,
    mass_kg: float,
    underwater_area_m2: float | None = None,
    longitude: float = 0.0,
    air_density: float = AIR_DENSITY_KG_M3,
    water_density: float = WATER_DENSITY_KG_M3,
    air_drag_coefficient: float = AIR_DRAG_COEFFICIENT,
    water_drag_coefficient: float = WATER_DRAG_COEFFICIENT,
    added_mass_factor: float = DEFAULT_ADDED_MASS_FACTOR,
) -> dict:
    """Return separate wind, water, Coriolis, and net acceleration terms."""
    _, _, velocity_u, velocity_v = state
    environment: Mapping[str, float] = environment_provider.at(latitude, longitude, time_seconds / 3600.0)
    wind_u = float(environment.get("wind_u_m_s", 0.0))
    wind_v = float(environment.get("wind_v_m_s", 0.0))
    current_u = float(environment.get("surface_current_u_m_s", environment.get("current_u_m_s", 0.0)))
    current_v = float(environment.get("surface_current_v_m_s", environment.get("current_v_m_s", 0.0)))
    relative_wind_u = wind_u - velocity_u
    relative_wind_v = wind_v - velocity_v
    relative_water_u = current_u - velocity_u
    relative_water_v = current_v - velocity_v
    relative_wind_speed = _vector_speed(relative_wind_u, relative_wind_v)
    relative_water_speed = _vector_speed(relative_water_u, relative_water_v)
    air_area = max(0.0, float(projected_area_m2))
    water_area = max(0.0, float(underwater_area_m2 if underwater_area_m2 is not None else projected_area_m2))
    wind_scale = 0.5 * air_density * air_drag_coefficient * air_area * relative_wind_speed
    water_scale = 0.5 * water_density * water_drag_coefficient * water_area * relative_water_speed
    wind_force_x = wind_scale * relative_wind_u
    wind_force_y = wind_scale * relative_wind_v
    water_force_x = water_scale * relative_water_u
    water_force_y = water_scale * relative_water_v
    effective_mass = max(1.0, float(mass_kg) * max(1.0, float(added_mass_factor)))
    f = coriolis_parameter(latitude)
    coriolis_acceleration_x = f * velocity_v
    coriolis_acceleration_y = -f * velocity_u
    wind_acceleration_x = wind_force_x / effective_mass
    wind_acceleration_y = wind_force_y / effective_mass
    water_acceleration_x = water_force_x / effective_mass
    water_acceleration_y = water_force_y / effective_mass
    net_acceleration_x = wind_acceleration_x + water_acceleration_x + coriolis_acceleration_x
    net_acceleration_y = wind_acceleration_y + water_acceleration_y + coriolis_acceleration_y
    return {
        "wind_speed": _vector_speed(wind_u, wind_v),
        "wind_direction": (math.degrees(math.atan2(wind_u, wind_v)) + 360.0) % 360.0,
        "current_speed": _vector_speed(current_u, current_v),
        "current_direction": (math.degrees(math.atan2(current_u, current_v)) + 360.0) % 360.0,
        "relative_wind_speed": relative_wind_speed,
        "relative_water_speed": relative_water_speed,
        "wind_force_x": wind_force_x,
        "wind_force_y": wind_force_y,
        "water_force_x": water_force_x,
        "water_force_y": water_force_y,
        "coriolis_acceleration_x": coriolis_acceleration_x,
        "coriolis_acceleration_y": coriolis_acceleration_y,
        "wind_acceleration_x": wind_acceleration_x,
        "wind_acceleration_y": wind_acceleration_y,
        "water_acceleration_x": water_acceleration_x,
        "water_acceleration_y": water_acceleration_y,
        "net_acceleration_x": net_acceleration_x,
        "net_acceleration_y": net_acceleration_y,
        "iceberg_speed": _vector_speed(velocity_u, velocity_v),
        "iceberg_heading": (math.degrees(math.atan2(velocity_u, velocity_v)) + 360.0) % 360.0,
        "effective_mass_kg": effective_mass,
        "air_projected_area_m2": air_area,
        "underwater_projected_area_m2": water_area,
    }


def compute_forces(time_seconds: float, state, latitude: float, environment_provider: Callable, height_m: float, projected_area_m2: float, mass_kg: float, underwater_area_m2: float | None = None, longitude: float = 0.0, **parameters):
    diagnostics = force_diagnostics(time_seconds, state, latitude, environment_provider, height_m, projected_area_m2, mass_kg, underwater_area_m2, longitude, **parameters)
    _, _, velocity_u, velocity_v = state
    return [velocity_u, velocity_v, diagnostics["net_acceleration_x"], diagnostics["net_acceleration_y"]]
