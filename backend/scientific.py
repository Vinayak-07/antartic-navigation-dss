from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import numpy as np
from scipy.integrate import solve_ivp

from backend.physics.coriolis import coriolis_parameter
from backend.physics.forces import compute_forces, force_diagnostics
from backend.physics.geometry import compute_geometry
from backend.utils.coordinates import DEFAULT_ANTARCTIC_MASK, SyntheticAntarcticMask


@dataclass(frozen=True)
class ScenarioParameters:
    ice_factor: float
    weather_factor: float
    iceberg_factor: float
    current_factor: float
    route_margin: float


SCENARIOS: Mapping[str, ScenarioParameters] = {
    "NORMAL": ScenarioParameters(1.0, 1.0, 1.0, 1.0, 1.0),
    "HEAVY_ICE": ScenarioParameters(1.42, 1.05, 1.05, 1.0, 1.22),
    "ICEBERG_ENCOUNTER": ScenarioParameters(1.08, 1.0, 2.0, 1.0, 1.35),
    "SEVERE_WEATHER": ScenarioParameters(1.0, 1.65, 1.0, 1.35, 1.3),
}


class SyntheticEnvironmentProvider:
    model_version = "synthetic-antarctic-1"

    def __init__(self, seed: int, scenario: str = "NORMAL", departure: datetime | None = None):
        self.seed = int(seed)
        self.scenario = scenario.upper()
        self.parameters = SCENARIOS.get(self.scenario, SCENARIOS["NORMAL"])
        phase = random.Random(self.seed).random() * math.tau
        self.phase = phase
        self.departure = departure

    def at(self, latitude: float, longitude: float, simulation_hours: float) -> Dict[str, float]:
        p = self.parameters
        lat_gradient = max(0.0, (abs(latitude) - 38.0) / 34.0)
        lon_wave = math.sin(math.radians(longitude * 2.7) + self.phase)
        lat_wave = math.cos(math.radians(latitude * 3.1) - self.phase * 0.7)
        temporal = math.sin(simulation_hours / 18.0 + self.phase) + 0.45 * math.cos(simulation_hours / 31.0 - self.phase)
        seasonal = math.cos(simulation_hours / 216.0 + self.phase * 0.2)
        smooth = 0.55 * lon_wave + 0.45 * lat_wave
        sst = 3.4 - 5.8 * lat_gradient + 0.45 * seasonal + 0.28 * smooth - 0.25 * (p.ice_factor - 1.0)
        temperature = sst - 1.8 * lat_gradient + 0.35 * temporal
        wind_speed = max(2.0, 11.0 + 3.8 * temporal + 2.2 * smooth + 8.0 * (p.weather_factor - 1.0))
        wind_direction = (148.0 + 24.0 * math.sin(math.radians(latitude)) + 18.0 * smooth + 10.0 * temporal) % 360.0
        pressure = 1008.0 - 8.5 * temporal - 5.0 * smooth - 8.0 * (p.weather_factor - 1.0)
        current_speed = max(0.05, (0.22 + 0.14 * lat_gradient + 0.09 * smooth) * p.current_factor)
        current_direction = (225.0 + 28.0 * lon_wave + 12.0 * seasonal) % 360.0
        wave_height = max(0.2, 0.65 + 0.105 * wind_speed + 0.22 * abs(temporal) * p.weather_factor)
        wave_direction = (wind_direction + 18.0 * math.sin(self.phase + simulation_hours / 24.0)) % 360.0
        wind_u, wind_v = self._vector(wind_speed, wind_direction)
        current_u, current_v = self._vector(current_speed, current_direction)
        return {
            "temperature_c": round(temperature, 4),
            "sea_surface_temperature_c": round(sst, 4),
            "wind_speed_m_s": round(wind_speed, 4),
            "wind_direction_deg": round(wind_direction, 4),
            "pressure_hpa": round(pressure, 4),
            "ocean_current_speed_m_s": round(current_speed, 4),
            "ocean_current_direction_deg": round(current_direction, 4),
            "surface_current_u_m_s": round(current_u, 4),
            "surface_current_v_m_s": round(current_v, 4),
            "wave_height_m": round(wave_height, 4),
            "wave_direction_deg": round(wave_direction, 4),
            "wind_u_m_s": round(wind_u, 4),
            "wind_v_m_s": round(wind_v, 4),
        }

    @staticmethod
    def _vector(speed: float, direction: float) -> Tuple[float, float]:
        angle = math.radians(direction)
        return speed * math.sin(angle), speed * math.cos(angle)


class SeaIceModel:
    model_version = "synthetic-sea-ice-1"

    def __init__(self, environment: SyntheticEnvironmentProvider):
        self.environment = environment
        self.parameters = environment.parameters

    def concentration(self, latitude: float, longitude: float, simulation_hours: float) -> float:
        env = self.environment.at(latitude, longitude, simulation_hours)
        latitude_term = max(0.0, (abs(latitude) - 48.0) / 23.0)
        coastal_band = math.exp(-((abs(latitude) - 67.0) / 8.5) ** 2)
        spatial = 0.08 * math.sin(math.radians(longitude * 3.0) + self.environment.phase) + 0.05 * math.cos(math.radians(latitude * 4.0))
        seasonal = 0.07 * math.sin(simulation_hours / 168.0 + self.environment.phase)
        thermal = max(0.0, -env["sea_surface_temperature_c"]) * 0.035
        value = 0.06 + 0.34 * latitude_term + 0.32 * coastal_band + spatial + seasonal + thermal
        return float(np.clip(value * self.parameters.ice_factor, 0.0, 1.0))

    def cell(self, latitude: float, longitude: float, simulation_hours: float, size: float = 3.0) -> Dict[str, object]:
        concentration = self.concentration(latitude, longitude, simulation_hours)
        thickness = 0.05 + 2.8 * concentration ** 1.25
        category = self.category(concentration)
        return {
            "center": [round(latitude, 4), round(longitude, 4)],
            "bounds": [[latitude - size / 2, longitude - size / 2], [latitude + size / 2, longitude + size / 2]],
            "concentration": round(concentration, 4),
            "thickness_m": round(thickness, 4),
            "category": category,
            "risk_score": round(float(np.clip(0.2 * concentration + 0.16 * thickness, 0.0, 1.0)), 4),
        }

    def grid(self, simulation_hours: float, latitude_range: Tuple[float, float] = (-72.0, -42.0), longitude_range: Tuple[float, float] = (8.0, 82.0), step: float = 4.0) -> List[Dict[str, object]]:
        cells = []
        latitude = latitude_range[0]
        while latitude <= latitude_range[1]:
            longitude = longitude_range[0]
            while longitude <= longitude_range[1]:
                cells.append(self.cell(latitude, longitude, simulation_hours, step))
                longitude += step
            latitude += step
        return cells

    @staticmethod
    def category(concentration: float) -> str:
        if concentration < 0.1:
            return "OPEN_WATER"
        if concentration < 0.3:
            return "VERY_OPEN_ICE"
        if concentration < 0.5:
            return "OPEN_ICE"
        if concentration < 0.7:
            return "CLOSE_ICE"
        if concentration < 0.9:
            return "VERY_CLOSE_ICE"
        return "FAST_ICE"


class IcebergModel:
    model_version = "synthetic-iceberg-rk45-1"

    def __init__(self, seed: int, scenario: str, environment: SyntheticEnvironmentProvider, land_mask: SyntheticAntarcticMask | None = None):
        self.seed = int(seed)
        self.parameters = SCENARIOS.get(scenario.upper(), SCENARIOS["NORMAL"])
        self.environment = environment
        self.land_mask = land_mask or DEFAULT_ANTARCTIC_MASK
        self.rng = random.Random(self.seed ^ 0x5F3759DF)
        self._integrated: Dict[str, Tuple[np.ndarray, np.ndarray, Dict[str, object]]] = {}
        self._grounded_overrides: Dict[str, Tuple[float, float, float]] = {}

    def generate(self, corridor: Sequence[Sequence[float]], count: int = 8) -> List[Dict[str, object]]:
        points = []
        for index in range(count):
            anchor = corridor[(index * 2 + self.rng.randrange(max(1, len(corridor)))) % len(corridor)]
            anchor_lat, anchor_lon = float(anchor[0]), float(anchor[1])
            if not self.land_mask.is_ocean(anchor_lat, anchor_lon, 100.0, 50.0):
                anchor_lat, anchor_lon = self.land_mask.nearest_ocean_position(anchor_lat, anchor_lon, 100.0, 50.0)
            latitude = float(anchor_lat - self.rng.uniform(-2.8, 2.8))
            longitude = float(anchor_lon + self.rng.uniform(-3.5, 3.5))
            length = self.rng.uniform(90.0, 420.0)
            width = length * self.rng.uniform(0.35, 0.75)
            height = self.rng.uniform(18.0, 55.0)
            if not self.land_mask.is_ocean(latitude, longitude, length, width):
                latitude, longitude = self.land_mask.nearest_ocean_position(latitude, longitude, length, width)
            geometry = compute_geometry(length, width, height)
            points.append({
                "id": f"IB-{self.seed % 1000:03d}-{index + 1:02d}",
                "lat": round(latitude, 5),
                "lon": round(longitude, 5),
                "length_m": round(length, 2),
                "width_m": round(width, 2),
                "height_m": round(height, 2),
                "estimated_mass_kg": round(geometry["mass_kg"], 2),
                "projected_area_m2": round(geometry["projected_area_m2"], 2),
                "air_projected_area_m2": round(geometry["air_projected_area_m2"], 2),
                "underwater_projected_area_m2": round(geometry["underwater_projected_area_m2"], 2),
                "effective_mass_kg": round(geometry["effective_mass_kg"], 2),
                "added_mass_factor": geometry["added_mass_factor"],
                "velocity_u_m_s": round(self.rng.uniform(-0.16, 0.16), 5),
                "velocity_v_m_s": round(self.rng.uniform(-0.16, 0.16), 5),
                "heading_deg": round(self.rng.uniform(0.0, 360.0), 2),
                "risk_radius_m": round(max(12000.0, length * 90.0), 2),
                "status": "DRIFTING",
            })
        return points

    def state_at(self, iceberg: Mapping[str, object], simulation_hours: float) -> Dict[str, object]:
        times, states, metadata = self._integrated_state(iceberg)
        target_hours = max(0.0, float(simulation_hours))
        values = [float(np.interp(target_hours, times, states[:, index])) for index in range(4)]
        x, y, u, v = values
        latitude = y / 111000.0
        longitude = x / 111000.0
        override = self._grounded_overrides.get(str(iceberg["id"]))
        if override and target_hours >= override[0]:
            _, latitude, longitude = override
            x = longitude * 111000.0
            y = latitude * 111000.0
            u = 0.0
            v = 0.0
        elif not self.land_mask.is_ocean(latitude, longitude, float(iceberg["length_m"]), float(iceberg["width_m"])):
            latitude, longitude = self.land_mask.nearest_ocean_position(latitude, longitude, float(iceberg["length_m"]), float(iceberg["width_m"]))
            self._grounded_overrides[str(iceberg["id"])] = (target_hours, latitude, longitude)
            x = longitude * 111000.0
            y = latitude * 111000.0
            u = 0.0
            v = 0.0
        heading = (math.degrees(math.atan2(u, v)) + 360.0) % 360.0
        state = dict(iceberg)
        grounded_at = metadata.get("grounded_at_hours")
        override = self._grounded_overrides.get(str(iceberg["id"]))
        is_grounded = (override and target_hours >= override[0]) or (grounded_at is not None and target_hours >= float(grounded_at))
        if is_grounded:
            status = "GROUNDED"
            u = 0.0
            v = 0.0
        else:
            dist_km = self.land_mask.distance_to_land_km(latitude, longitude)
            status = "COASTAL" if dist_km <= 35.0 else "DRIFTING"

        state.update({"lat": round(latitude, 5), "lon": round(longitude, 5), "velocity_u_m_s": round(float(u), 5), "velocity_v_m_s": round(float(v), 5), "heading_deg": round(heading, 2), "risk_level": self.risk_level(float(iceberg["risk_radius_m"])), "status": status})
        state["physics_diagnostics"] = force_diagnostics(
            target_hours * 3600.0,
            [x, y, u, v],
            latitude,
            self.environment,
            float(iceberg["height_m"]),
            float(iceberg["air_projected_area_m2"]),
            float(iceberg["estimated_mass_kg"]),
            float(iceberg["underwater_projected_area_m2"]),
            longitude,
        )
        if status in {"COASTAL", "GROUNDED"}:
            if status == "GROUNDED":
                state["physics_diagnostics"].update({"net_acceleration_x": 0.0, "net_acceleration_y": 0.0, "coastal_constraint_acceleration_x": -state["physics_diagnostics"]["net_acceleration_x"], "coastal_constraint_acceleration_y": -state["physics_diagnostics"]["net_acceleration_y"], "iceberg_speed": 0.0, "iceberg_heading": 0.0})
                state["grounded_at_hours"] = float(override[0] if override else metadata["grounded_at_hours"])
        return state

    def _integrated_state(self, iceberg: Mapping[str, object]) -> Tuple[np.ndarray, np.ndarray, Dict[str, object]]:
        identifier = str(iceberg["id"])
        if identifier in self._integrated:
            return self._integrated[identifier]
        initial = [float(iceberg["lon"]) * 111000.0, float(iceberg["lat"]) * 111000.0, float(iceberg["velocity_u_m_s"]), float(iceberg["velocity_v_m_s"])]
        times = np.arange(0.0, 321.0, 1.0)

        def derivative(time_hours, state):
            current_latitude = state[1] / 111000.0
            current_longitude = state[0] / 111000.0
            cos_lat = max(0.05, math.cos(math.radians(current_latitude)))
            position_u, position_v, acceleration_u, acceleration_v = compute_forces(time_hours * 3600.0, state, current_latitude, self.environment, float(iceberg["height_m"]), float(iceberg["air_projected_area_m2"]), float(iceberg["estimated_mass_kg"]), float(iceberg["underwater_projected_area_m2"]), current_longitude)
            return [(position_u / cos_lat) * 3600.0, position_v * 3600.0, acceleration_u * 3600.0, acceleration_v * 3600.0]

        result = solve_ivp(derivative, (times[0], times[-1]), initial, t_eval=times, method="RK45", rtol=2e-4, atol=[1.0, 1.0, 1e-4, 1e-4], max_step=6.0)
        constrained_states, metadata = constrain_trajectory_states(result.y.T, times, iceberg, self.land_mask)
        self._integrated[identifier] = (times, constrained_states, metadata)
        return self._integrated[identifier]

    def trajectory(self, iceberg: Mapping[str, object], simulation_hours: float) -> Dict[str, object]:
        positions = []
        grounded_at = None
        grounded_coordinate = None
        for offset in (0, 6, 12, 24, 48, 72):
            target_time = simulation_hours + offset
            state = self.state_at(iceberg, target_time)
            if state["status"] == "GROUNDED" and grounded_at is None:
                grounded_at = offset
                grounded_coordinate = [state["lon"], state["lat"]]
            if grounded_coordinate is not None and grounded_at is not None and offset >= grounded_at:
                coordinates = grounded_coordinate
            else:
                coordinates = [state["lon"], state["lat"]]
            positions.append({"time_hours": offset, "coordinates": coordinates})
        metadata = self._integrated_state(iceberg)[2]
        status = "GROUNDED" if grounded_at is not None or metadata["status"] == "GROUNDED" else "DRIFTING"
        return {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [item["coordinates"] for item in positions]}, "properties": {"id": iceberg["id"], "horizons_hours": [6, 12, 24, 48, 72], "status": status, "grounded_at_hours": grounded_at if grounded_at is not None else metadata.get("grounded_at_hours")}}

    @staticmethod
    def risk_level(radius: float) -> str:
        if radius >= 28000:
            return "high"
        if radius >= 18000:
            return "moderate"
        return "low"


def constrain_trajectory_states(states: np.ndarray, times: np.ndarray, iceberg: Mapping[str, object], land_mask: SyntheticAntarcticMask) -> Tuple[np.ndarray, Dict[str, object]]:
    """Stop the first RK45 state that would place the iceberg footprint on land."""
    constrained = np.array(states, dtype=float, copy=True)
    length = float(iceberg.get("length_m", 100.0))
    width = float(iceberg.get("width_m", 50.0))

    def geographic_position(state):
        latitude = state[1] / 111000.0
        longitude = state[0] / 111000.0
        return latitude, longitude

    def valid(state):
        latitude, longitude = geographic_position(state)
        return land_mask.is_ocean(latitude, longitude, length, width) and land_mask.is_ocean(round(latitude, 5), round(longitude, 5), length, width)

    # 1. Validate initial condition at t=0
    if not valid(constrained[0]):
        lat, lon = geographic_position(constrained[0])
        valid_lat, valid_lon = land_mask.nearest_ocean_position(lat, lon, length, width)
        clamped_state = np.array([valid_lon * 111000.0, valid_lat * 111000.0, 0.0, 0.0], dtype=float)
        constrained[:] = clamped_state
        return constrained, {"status": "GROUNDED", "grounded_at_hours": 0.0}

    # 2. Sequential segment validation
    for index in range(1, len(constrained)):
        if valid(constrained[index]):
            continue
        previous = constrained[index - 1].copy()
        invalid = constrained[index].copy()
        for _ in range(18):
            midpoint = (previous + invalid) / 2.0
            if valid(midpoint):
                previous = midpoint
            else:
                invalid = midpoint
        boundary_state = previous.copy()
        boundary_state[2:] = 0.0
        lat, lon = geographic_position(boundary_state)
        if not land_mask.is_ocean(round(lat, 5), round(lon, 5), length, width):
            safe_lat, safe_lon = land_mask.nearest_ocean_position(lat, lon, length, width)
            boundary_state[0] = safe_lon * 111000.0
            boundary_state[1] = safe_lat * 111000.0
        constrained[index:] = boundary_state
        return constrained, {"status": "GROUNDED", "grounded_at_hours": float(times[index])}
    return constrained, {"status": "DRIFTING", "grounded_at_hours": None}


def distance_km(first: Sequence[float], second: Sequence[float]) -> float:
    latitude = math.radians((first[0] + second[0]) / 2.0)
    dlat = (second[0] - first[0]) * 111.0
    dlon = (second[1] - first[1]) * 111.0 * math.cos(latitude)
    return math.hypot(dlat, dlon)


def interpolate_route(route: Sequence[Sequence[float]], distance: float) -> Tuple[float, float, float]:
    remaining = max(0.0, distance)
    for first, second in zip(route, route[1:]):
        segment = distance_km(first, second)
        if remaining <= segment or segment == 0:
            ratio = 0.0 if segment == 0 else remaining / segment
            latitude = first[0] + (second[0] - first[0]) * ratio
            longitude = first[1] + (second[1] - first[1]) * ratio
            heading = (math.degrees(math.atan2((second[1] - first[1]) * math.cos(math.radians(latitude)), second[0] - first[0])) + 360.0) % 360.0
            return latitude, longitude, heading
        remaining -= segment
    return float(route[-1][0]), float(route[-1][1]), 0.0


def route_distance(route: Sequence[Sequence[float]]) -> float:
    return round(sum(distance_km(first, second) for first, second in zip(route, route[1:])), 2)


def _point_to_segment_distance_km(point: Sequence[float], first: Sequence[float], second: Sequence[float]) -> float:
    latitude_scale = 111.0
    longitude_scale = 111.0 * math.cos(math.radians(point[0]))
    px, py = point[1] * longitude_scale, point[0] * latitude_scale
    ax, ay = first[1] * longitude_scale, first[0] * latitude_scale
    bx, by = second[1] * longitude_scale, second[0] * latitude_scale
    dx, dy = bx - ax, by - ay
    denominator = dx * dx + dy * dy
    ratio = 0.0 if denominator == 0.0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denominator))
    return math.hypot(px - (ax + ratio * dx), py - (ay + ratio * dy))


def iceberg_route_risk(iceberg: Mapping[str, object], route: Sequence[Sequence[float]], trajectory: Mapping[str, object] | None = None) -> Dict[str, object]:
    coordinates = []
    if trajectory and trajectory.get("geometry", {}).get("coordinates"):
        coordinates.extend(trajectory["geometry"]["coordinates"])
    coordinates.append([float(iceberg["lon"]), float(iceberg["lat"])])
    route_points = [[float(point[0]), float(point[1])] for point in route]
    minimum_distance = float("inf")
    closest_time = 0
    horizons = (trajectory or {}).get("properties", {}).get("horizons_hours", [])
    for index, coordinate in enumerate(coordinates):
        point = [float(coordinate[1]), float(coordinate[0])]
        for first, second in zip(route_points, route_points[1:]):
            minimum_distance = min(minimum_distance, _point_to_segment_distance_km(point, first, second))
        if minimum_distance == minimum_distance and index < len(horizons):
            closest_time = horizons[index]
    radius_km = max(1.0, float(iceberg["risk_radius_m"]) / 1000.0)
    proximity = max(0.0, 1.0 - minimum_distance / radius_km)
    size_factor = min(1.0, float(iceberg.get("length_m", 0.0)) / 350.0)
    score = float(np.clip(proximity * (0.65 + 0.35 * size_factor), 0.0, 1.0))
    level = "HIGH" if score >= 0.7 else "MODERATE" if score >= 0.3 else "LOW"
    return {"risk_score": round(score, 4), "risk_level": level, "minimum_distance_km": round(minimum_distance, 2), "risk_radius_km": round(radius_km, 2), "closest_horizon_hours": closest_time, "route_conflict": minimum_distance <= radius_km}


def build_routes(origin: Sequence[float], destination: Sequence[float], ice: SeaIceModel, bergs: Sequence[Mapping[str, object]], environment: SyntheticEnvironmentProvider, simulation_hours: float, iceberg_model: IcebergModel = None, vessel_ice_class: str = "PC6") -> Dict[str, Dict[str, object]]:
    from backend.routing.astar import find_route
    from backend.routing.cost_grid import build_cost_grid
    from backend.routing.route_scoring import score_route
    midpoint = [(origin[0] + destination[0]) / 2.0, (origin[1] + destination[1]) / 2.0]
    reference_shortest = [list(origin), [midpoint[0] + 4.5, midpoint[1] - 7.0], list(destination)]
    reference_conservative = [list(origin), [midpoint[0] - 3.0, midpoint[1] - 13.0], [destination[0] + 1.8, destination[1] - 5.0], list(destination)]
    
    # Build iceberg trajectories for future risk evaluation
    iceberg_trajectories = {}
    if iceberg_model:
        for berg in bergs:
            iceberg_trajectories[berg["id"]] = iceberg_model.trajectory(berg, simulation_hours)
    
    grid = build_cost_grid(origin, destination, ice, bergs, environment, simulation_hours, iceberg_trajectories=iceberg_trajectories, vessel_ice_class=vessel_ice_class)
    optimized = find_route(grid, reference_shortest[0], reference_shortest[-1], avoid_margin=8.0) or reference_shortest
    if len(optimized) < 2:
        optimized = reference_shortest
    routes = {}
    for key, name, points in (("reference_shortest", "Reference / shortest", reference_shortest), ("optimized", "Recommended", optimized), ("reference_conservative", "Conservative", reference_conservative)):
        score = score_route(points, ice, bergs, environment, simulation_hours)
        routes[key] = {"name": name, "points": points, **score}
    return routes


# ============================================================
# VESSEL DYNAMICS
# ============================================================

@dataclass(frozen=True)
class VesselConfig:
    """Vessel performance parameters."""
    cruise_speed_kn: float = 17.0
    max_speed_kn: float = 20.0
    max_acceleration_kn_per_hr: float = 5.0    # knots per hour
    max_deceleration_kn_per_hr: float = 8.0    # knots per hour
    max_turn_rate_deg_per_hr: float = 45.0     # degrees per hour
    ice_capability: str = "PC6"                # Polar Class
    fuel_capacity_tonnes: float = 500.0
    fuel_consumption_base_tonnes_per_nm: float = 0.052


DEFAULT_VESSEL_CONFIG = VesselConfig()


def interpolate_heading(current: float, target: float, max_turn_deg: float) -> float:
    """Smoothly interpolate heading toward target with turn rate limit."""
    diff = (target - current + 180.0) % 360.0 - 180.0
    if abs(diff) <= max_turn_deg:
        return target
    return (current + (max_turn_deg if diff > 0 else -max_turn_deg) + 360.0) % 360.0


def interpolate_speed(current: float, target: float, max_accel: float, max_decel: float, dt_hours: float) -> float:
    """Smoothly interpolate speed toward target with acceleration limits."""
    max_speed_change = max_accel * dt_hours if target > current else max_decel * dt_hours
    diff = target - current
    if abs(diff) <= max_speed_change:
        return target
    return current + (max_speed_change if diff > 0 else -max_speed_change)


def compute_vessel_state(
    prev_state: Dict[str, float],
    route: Sequence[Sequence[float]],
    distance_along_route: float,
    dt_hours: float,
    config: VesselConfig = DEFAULT_VESSEL_CONFIG,
) -> Dict[str, float]:
    """
    Compute smooth vessel state (position, heading, speed) given route progress.

    Args:
        prev_state: Previous vessel state with keys: lat, lon, heading_deg, speed_kn
        route: Route points [[lat, lon], ...]
        distance_along_route: Distance travelled along route in km
        dt_hours: Time step in hours
        config: Vessel configuration

    Returns:
        Updated vessel state dict
    """
    # Get target position and heading from route
    target_lat, target_lon, target_heading = interpolate_route(route, distance_along_route)

    # Current state
    current_lat = prev_state.get("lat", target_lat)
    current_lon = prev_state.get("lon", target_lon)
    current_heading = prev_state.get("heading_deg", target_heading)
    current_speed = prev_state.get("speed_kn", config.cruise_speed_kn)

    # Smooth heading transition
    max_turn = config.max_turn_rate_deg_per_hr * dt_hours
    new_heading = interpolate_heading(current_heading, target_heading, max_turn)

    # Smooth speed transition (target is cruise speed unless in heavy ice)
    target_speed = config.cruise_speed_kn
    max_accel = config.max_acceleration_kn_per_hr * dt_hours
    max_decel = config.max_deceleration_kn_per_hr * dt_hours
    new_speed = interpolate_speed(current_speed, target_speed, max_accel, max_decel, dt_hours)

    # Compute new position using current speed and heading (dead reckoning)
    # This gives smoother movement than snapping to route
    if dt_hours > 0:
        speed_kmh = new_speed * 1.852  # knots to km/h
        dist_km = speed_kmh * dt_hours
        heading_rad = math.radians(new_heading)
        lat_change = (dist_km / 111.0) * math.cos(heading_rad)
        lon_change = (dist_km / (111.0 * max(0.1, math.cos(math.radians(current_lat))))) * math.sin(heading_rad)
        new_lat = current_lat + lat_change
        new_lon = current_lon + lon_change
        # Cross-track correction: nudge back toward route target proportional
        # to drift magnitude (dead-reckoning accumulates error over time)
        target_lat, target_lon, _ = interpolate_route(route, distance_along_route)
        lat_drift = target_lat - new_lat
        lon_drift = target_lon - new_lon
        # Proportional correction — stronger the farther off
        correction_factor = min(0.35, 0.08 * max(1.0, dt_hours))
        new_lat += lat_drift * correction_factor
        new_lon += lon_drift * correction_factor
    else:
        new_lat, new_lon = target_lat, target_lon

    return {
        "lat": new_lat,
        "lon": new_lon,
        "heading_deg": new_heading,
        "speed_kn": new_speed,
        "target_heading_deg": target_heading,
        "target_speed_kn": target_speed,
    }


def estimate_fuel_consumption(
    distance_km: float,
    avg_speed_kn: float,
    sea_ice_risk: float,
    weather_risk: float,
    config: VesselConfig = DEFAULT_VESSEL_CONFIG,
) -> float:
    """Estimate fuel consumption in tonnes."""
    base_consumption = distance_km * config.fuel_consumption_base_tonnes_per_nm
    # Increased consumption in ice and bad weather
    ice_factor = 1.0 + sea_ice_risk * 0.5
    weather_factor = 1.0 + weather_risk * 0.3
    speed_factor = max(1.0, avg_speed_kn / config.cruise_speed_kn)
    return base_consumption * ice_factor * weather_factor * speed_factor


def risk_at(latitude: float, longitude: float, simulation_hours: float, ice: SeaIceModel, bergs: Iterable[Mapping[str, object]], environment: SyntheticEnvironmentProvider) -> Dict[str, object]:
    env = environment.at(latitude, longitude, simulation_hours)
    concentration = ice.concentration(latitude, longitude, simulation_hours)
    thickness = 0.05 + 2.8 * concentration ** 1.25
    sea_ice_risk = float(np.clip(0.55 * concentration + 0.12 * thickness, 0.0, 1.0))
    iceberg_risk = 0.0
    nearest = None
    for iceberg in bergs:
        distance = distance_km((latitude, longitude), (float(iceberg["lat"]), float(iceberg["lon"]))) * 1000.0
        factor = max(0.0, 1.0 - distance / max(1.0, float(iceberg["risk_radius_m"])))
        candidate = factor * min(1.0, float(iceberg["length_m"]) / 350.0)
        if candidate > iceberg_risk:
            iceberg_risk = candidate
            nearest = iceberg["id"]
    weather_risk = float(np.clip(0.025 * max(0.0, env["wind_speed_m_s"] - 12.0) + 0.12 * max(0.0, env["wave_height_m"] - 2.0) + 0.004 * abs(env["pressure_hpa"] - 1010.0), 0.0, 1.0))
    overall = float(np.clip(0.42 * sea_ice_risk + 0.38 * iceberg_risk + 0.20 * weather_risk, 0.0, 1.0))
    return {"sea_ice_risk": round(sea_ice_risk, 4), "iceberg_risk": round(iceberg_risk, 4), "weather_risk": round(weather_risk, 4), "overall_navigation_risk": round(overall, 4), "status": "HIGH" if overall >= 0.7 else "WATCH" if overall >= 0.45 else "LOW", "nearest_iceberg_id": nearest, "sea_ice_concentration": round(concentration, 4), "sea_ice_thickness_m": round(thickness, 4)}
