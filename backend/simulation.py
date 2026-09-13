from __future__ import annotations

import random
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.scientific import (
    SCENARIOS,
    IcebergModel,
    SeaIceModel,
    SyntheticEnvironmentProvider,
    build_routes,
    distance_km,
    interpolate_route,
    risk_at,
    iceberg_route_risk,
    route_distance,
)

VORIGIN_COORDS = {
    "Cape Town": {"lat": -33.9249, "lon": 18.4241},
    "Bharati Station": {"lat": -69.405, "lon": 76.186},
    "Maitri Station": {"lat": -70.7667, "lon": 11.7333},
}


class TripEngine:
    """In-memory lifecycle owner for reproducible synthetic voyage simulations."""

    def __init__(self):
        self.trips: Dict[str, Dict[str, Any]] = {}
        self.models: Dict[str, Dict[str, Any]] = {}

    def create_trip(self, vessel: str, origin: str, destination: str, scenario: str = "NORMAL", departure_time: Optional[str] = None, seed: Optional[int] = None, trip_id: Optional[str] = None) -> Dict[str, Any]:
        trip_id = trip_id or f"TRIP-{uuid.uuid4().hex[:8].upper()}"
        scenario_key = scenario.upper() if scenario.upper() in SCENARIOS else "NORMAL"
        seed = random.SystemRandom().randint(1, 999999) if seed is None else int(seed)
        trip = {
            "id": trip_id,
            "scenario": scenario_key,
            "seed": seed,
            "model_version": "synthetic-antarctic-1",
            "vessel": vessel,
            "origin": origin,
            "destination": destination,
            "departure_time": self._parse_datetime(departure_time).isoformat(),
            "simulation_start": 0.0,
            "simulation_end": 240.0,
            "current_simulation_time": 0.0,
            "status": "NEW",
            "phase": "READY",
            "speed": 1.0,
            "timeline": [],
            "events": [],
            "vessel_state": {},
            "environment": {},
            "sea_ice": {},
            "iceberg_states": [],
            "routes": {},
            "active_route": "optimized",
            "risk": {},
            "distance_km": 0.0,
            "fuel_remaining": 100.0,
            "duration_hours": 0.0,
            "replay_mode": False,
            "source_trip_id": None,
            "route_change": None,
        }
        self.trips[trip_id] = trip
        self._initialize_trip(trip)
        return deepcopy(trip)

    def create_trip_from_point(self, source_trip_id: str, target_time: Optional[float] = None, vessel: Optional[str] = None, origin: Optional[str] = None, destination: Optional[str] = None) -> Dict[str, Any]:
        source = self.trips[source_trip_id]
        trip = self.create_trip(vessel or source["vessel"], origin or source["origin"], destination or source["destination"], source["scenario"], source["departure_time"], int(source["seed"]) + 7)
        trip["source_trip_id"] = source_trip_id
        self._seek_to_time(trip, float(target_time if target_time is not None else source["current_simulation_time"]))
        self._record_event(trip, "ROUTE_CALCULATED", "normal", "Trip continuation created", "Historical route preserved for continued replay", "Continue from selected point", {"source_trip_id": source_trip_id})
        self.trips[trip["id"]] = trip
        return deepcopy(trip)

    def list_trips(self) -> List[Dict[str, Any]]:
        return [deepcopy(trip) for trip in self.trips.values()]

    def get_trip(self, trip_id: str) -> Dict[str, Any]:
        return deepcopy(self.trips[trip_id])

    def start_trip(self, trip_id: str) -> Dict[str, Any]:
        trip = self.trips[trip_id]
        trip["status"] = "RUNNING"
        trip["phase"] = self._phase_for_time(trip["current_simulation_time"], trip)
        trip["replay_mode"] = False
        self._record_event(trip, "VOYAGE_STARTED", "normal", "Voyage started", "Synthetic voyage playback begins", "Departure state accepted", {"route": trip["active_route"]})
        return deepcopy(trip)

    def pause_trip(self, trip_id: str) -> Dict[str, Any]:
        trip = self.trips[trip_id]
        trip["status"] = "PAUSED"
        trip["phase"] = "READY"
        return deepcopy(trip)

    def reset_trip(self, trip_id: str) -> Dict[str, Any]:
        trip = self.trips[trip_id]
        trip["status"] = "NEW"
        trip["phase"] = "READY"
        trip["current_simulation_time"] = 0.0
        trip["replay_mode"] = False
        self._initialize_trip(trip)
        return deepcopy(trip)

    def step_trip(self, trip_id: str, steps: int = 1) -> Dict[str, Any]:
        trip = self.trips[trip_id]
        for _ in range(max(1, int(steps))):
            self._advance_trip(trip, 1.0)
        return deepcopy(trip)

    def set_speed(self, trip_id: str, speed: float) -> Dict[str, Any]:
        self.trips[trip_id]["speed"] = max(0.5, min(50.0, float(speed)))
        return deepcopy(self.trips[trip_id])

    def seek_trip(self, trip_id: str, target_time: float) -> Dict[str, Any]:
        trip = self.trips[trip_id]
        trip["status"] = "REPLAY"
        trip["phase"] = "REPLAY"
        trip["replay_mode"] = True
        self._seek_to_time(trip, target_time)
        return deepcopy(trip)

    def get_trip_state(self, trip_id: str) -> Dict[str, Any]:
        self.tick_trip(trip_id)
        return self._snapshot(self.trips[trip_id])

    def tick_trip(self, trip_id: str) -> None:
        trip = self.trips[trip_id]
        if trip["status"] == "RUNNING":
            self._advance_trip(trip, max(1.0, round(float(trip["speed"]))))

    def get_trip_timeline(self, trip_id: str) -> List[Dict[str, Any]]:
        return deepcopy(self.trips[trip_id]["timeline"])

    def get_trip_events(self, trip_id: str) -> List[Dict[str, Any]]:
        return deepcopy(self.trips[trip_id]["events"])

    def _initialize_trip(self, trip: Dict[str, Any]) -> None:
        origin = VORIGIN_COORDS.get(trip["origin"], VORIGIN_COORDS["Cape Town"])
        destination = VORIGIN_COORDS.get(trip["destination"], VORIGIN_COORDS["Bharati Station"])
        departure = self._parse_datetime(trip["departure_time"])
        environment = SyntheticEnvironmentProvider(trip["seed"], trip["scenario"], departure)
        sea_ice = SeaIceModel(environment)
        corridor = [[origin["lat"], origin["lon"]], [(origin["lat"] + destination["lat"]) / 2.0, (origin["lon"] + destination["lon"]) / 2.0], [destination["lat"], destination["lon"]]]
        iceberg_model = IcebergModel(trip["seed"], trip["scenario"], environment)
        icebergs = iceberg_model.generate(corridor, 10)
        if trip["scenario"] == "ICEBERG_ENCOUNTER":
            icebergs[0]["lat"] = corridor[1][0] + 0.3
            icebergs[0]["lon"] = corridor[1][1] + 0.3
            icebergs[0]["risk_radius_m"] = max(icebergs[0]["risk_radius_m"], 50000.0)
        routes_one_way = build_routes([origin["lat"], origin["lon"]], [destination["lat"], destination["lon"]], sea_ice, icebergs, environment, 0.0)
        routes = {}
        for key, route in routes_one_way.items():
            points = route["points"] + [list(point) for point in reversed(route["points"][:-1])]
            route_data = dict(route)
            route_data["points"] = points
            route_data["distance_km"] = route_distance(points)
            route_data["travel_time_hours"] = round(route_data["distance_km"] / (17.0 * 1.852), 2)
            route_data["estimated_duration_hours"] = route_data["travel_time_hours"]
            route_data["fuel_tonnes"] = round(route_data["distance_km"] * 0.052, 2)
            routes[key] = route_data
        self.models[trip["id"]] = {"environment": environment, "sea_ice": sea_ice, "iceberg": iceberg_model, "initial_icebergs": icebergs, "origin": origin, "destination": destination}
        trip["routes"] = routes
        trip["active_route"] = "optimized"
        trip["events"] = []
        trip["route_change"] = None
        trip["current_simulation_time"] = 0.0
        trip["distance_km"] = 0.0
        trip["duration_hours"] = 0.0
        trip["fuel_remaining"] = 100.0
        trip["vessel_state"] = {"name": trip["vessel"], "lat": origin["lat"], "lon": origin["lon"], "speed_kn": 17.0, "heading_deg": 132.0, "fuel_capacity_tonnes": routes["optimized"]["fuel_tonnes"] * 1.18, "fuel_remaining_tonnes": routes["optimized"]["fuel_tonnes"] * 1.18, "fuel_remaining_pct": 100.0, "fuel_consumption_tonnes_per_hour": 0.052 * 17.0 * 1.852, "eta_hours": routes["optimized"]["travel_time_hours"], "risk_state": "LOW", "status": "READY"}
        trip["environment"] = environment.at(origin["lat"], origin["lon"], 0.0)
        trip["sea_ice"] = {"concentration": sea_ice.concentration(origin["lat"], origin["lon"], 0.0), "risk_level": "Open Water", "confidence": 0.82, "forecast_horizon_days": 10, "grid": sea_ice.grid(0.0)}
        trip["iceberg_states"] = [iceberg_model.state_at(item, 0.0) for item in icebergs]
        initial_trajectories = {item["id"]: iceberg_model.trajectory(item, 0.0) for item in icebergs}
        for iceberg in trip["iceberg_states"]:
            if iceberg.get("status") == "GROUNDED" and not any(event["event_type"] == "ICEBERG_GROUNDED" and event.get("related_objects", {}).get("iceberg_id") == iceberg["id"] for event in trip["events"]):
                self._record_event(trip, "ICEBERG_GROUNDED", "warning", "Iceberg grounded", "The iceberg reached the synthetic Antarctic coastal boundary and was prevented from entering land.", "Land-mask footprint intersection", {"iceberg_id": iceberg["id"], "latitude": iceberg["lat"], "longitude": iceberg["lon"], "status": iceberg["status"]})
        self._apply_route_risk(trip, routes["optimized"]["points"], trip["iceberg_states"], initial_trajectories)
        trip["risk"] = risk_at(origin["lat"], origin["lon"], 0.0, sea_ice, trip["iceberg_states"], environment)
        self._record_event(trip, "ROUTE_CALCULATED", "normal", "Initial route generated", "Round-trip route candidates generated from the seeded model state", "Dynamic cost grid evaluated", {"route": "optimized"})
        trip["timeline"] = [self._snapshot(trip)]

    def _advance_trip(self, trip: Dict[str, Any], hours: float) -> None:
        if trip["current_simulation_time"] >= trip["simulation_end"]:
            trip["status"] = "COMPLETED"
            trip["phase"] = "ARRIVED"
            return
        trip["current_simulation_time"] = min(trip["simulation_end"], trip["current_simulation_time"] + hours)
        self._update_trip(trip)
        trip["timeline"].append(self._snapshot(trip))

    def _update_trip(self, trip: Dict[str, Any]) -> None:
        model = self.models[trip["id"]]
        time = trip["current_simulation_time"]
        route = trip["routes"][trip["active_route"]]["points"]
        full_distance = route_distance(route)
        distance = min(full_distance, time * 17.0 * 1.852)
        latitude, longitude, heading = interpolate_route(route, distance)
        trip["distance_km"] = round(distance, 2)
        trip["duration_hours"] = float(time)
        trip["fuel_remaining"] = max(0.0, 100.0 - distance / max(1.0, full_distance) * 100.0)
        environment = model["environment"].at(latitude, longitude, time)
        sea_ice = model["sea_ice"]
        icebergs = [model["iceberg"].state_at(item, time) for item in model["initial_icebergs"]]
        for iceberg in icebergs:
            if iceberg.get("status") == "GROUNDED" and not any(event["event_type"] == "ICEBERG_GROUNDED" and event.get("related_objects", {}).get("iceberg_id") == iceberg["id"] for event in trip["events"]):
                self._record_event(trip, "ICEBERG_GROUNDED", "warning", "Iceberg grounded", "The iceberg reached the synthetic Antarctic coastal boundary and was prevented from entering land.", "Land-mask footprint intersection", {"iceberg_id": iceberg["id"], "latitude": iceberg["lat"], "longitude": iceberg["lon"], "status": iceberg["status"]})
        risk = risk_at(latitude, longitude, time, sea_ice, icebergs, model["environment"])
        trajectory_by_id = {item["id"]: model["iceberg"].trajectory(item, time) for item in model["initial_icebergs"]}
        route_risk = self._apply_route_risk(trip, route, icebergs, trajectory_by_id)
        scenario_trigger = (trip["scenario"] == "ICEBERG_ENCOUNTER" and time >= 24.0) or (trip["scenario"] == "HEAVY_ICE" and time >= 48.0) or (trip["scenario"] == "SEVERE_WEATHER" and time >= 18.0)
        if (risk["overall_navigation_risk"] >= 0.58 or scenario_trigger) and trip["active_route"] == "optimized" and time >= 12.0 and not any(event["event_type"] == "ROUTE_RECALCULATED" for event in trip["events"]):
            previous = trip["active_route"]
            trip["active_route"] = "conservative"
            trip["route_change"] = {"trigger": "Predicted iceberg and sea-ice corridor exposure", "previous_route": previous, "new_route": "conservative", "risk_before": risk["overall_navigation_risk"], "risk_after": max(0.0, risk["overall_navigation_risk"] - 0.18), "additional_distance_km": round(trip["routes"]["conservative"]["distance_km"] - trip["routes"][previous]["distance_km"], 2), "additional_fuel_tonnes": round(trip["routes"]["conservative"]["fuel_tonnes"] - trip["routes"][previous]["fuel_tonnes"], 2), "explanation": "Route changed because an evolving iceberg corridor and local sea-ice concentration increased exposure."}
            self._record_event(trip, "ROUTE_RECALCULATED", "warning", "Route recalculated", trip["route_change"]["explanation"], trip["route_change"]["trigger"], trip["route_change"])
            route = trip["routes"][trip["active_route"]]["points"]
            full_distance = route_distance(route)
            distance = min(full_distance, time * 17.0 * 1.852)
            latitude, longitude, heading = interpolate_route(route, distance)
            risk = risk_at(latitude, longitude, time, sea_ice, icebergs, model["environment"])
            route_risk = self._apply_route_risk(trip, route, icebergs, trajectory_by_id)
        phase = self._phase_for_time(time, trip)
        if phase == "RETURN" and not any(event["event_type"] == "RETURN_STARTED" for event in trip["events"]):
            self._record_event(trip, "RETURN_STARTED", "normal", "Return voyage started", "The same evolving environment continues on the return leg", "Destination waypoint reached", {"destination": trip["destination"]})
        trip["phase"] = phase
        trip["environment"] = environment
        trip["sea_ice"] = {"concentration": risk["sea_ice_concentration"], "risk_level": model["sea_ice"].category(risk["sea_ice_concentration"]), "confidence": 0.82, "forecast_horizon_days": 10, "grid": model["sea_ice"].grid(time)}
        trip["iceberg_states"] = icebergs
        trip["risk"] = risk
        trip["vessel_state"].update({"lat": round(latitude, 5), "lon": round(longitude, 5), "heading_deg": round(heading, 2), "speed_kn": 17.0, "fuel_remaining_pct": round(trip["fuel_remaining"], 2), "fuel_remaining_tonnes": round(trip["routes"][trip["active_route"]]["fuel_tonnes"] * trip["fuel_remaining"] / 100.0, 2), "eta_hours": round(max(0.0, (full_distance - distance) / (17.0 * 1.852)), 2), "risk_state": risk["status"], "status": "UNDERWAY"})
        if time >= trip["simulation_end"]:
            trip["status"] = "COMPLETED"
            trip["phase"] = "ARRIVED"
            self._record_event(trip, "VOYAGE_COMPLETED", "normal", "Voyage completed", "The round-trip route reached the origin", "Return route completed", {"origin": trip["origin"]})

    def _apply_route_risk(self, trip: Dict[str, Any], route: List[List[float]], icebergs: List[Dict[str, Any]], trajectories: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        risks = {}
        for iceberg in icebergs:
            assessment = iceberg_route_risk(iceberg, route, trajectories.get(iceberg["id"]))
            iceberg["route_risk"] = assessment
            iceberg["route_conflict"] = assessment["route_conflict"]
            iceberg["risk_reason"] = "Predicted trajectory enters the active route risk radius" if assessment["route_conflict"] else "Predicted trajectory remains outside the active route risk radius"
            risks[iceberg["id"]] = assessment
            event_type = "ICEBERG_ROUTE_CONFLICT" if assessment["risk_level"] == "HIGH" else "ICEBERG_APPROACHING_ROUTE" if assessment["risk_level"] == "MODERATE" else None
            if event_type and not any(event["event_type"] == event_type and event.get("related_objects", {}).get("iceberg_id") == iceberg["id"] for event in trip["events"]):
                self._record_event(trip, event_type, "warning" if event_type == "ICEBERG_ROUTE_CONFLICT" else "normal", "Iceberg route conflict" if event_type == "ICEBERG_ROUTE_CONFLICT" else "Iceberg approaching route", iceberg["risk_reason"], "Route proximity threshold evaluated", {"iceberg_id": iceberg["id"], "risk": assessment})
        return risks

    def _seek_to_time(self, trip: Dict[str, Any], target_time: float) -> None:
        target = max(0.0, min(float(target_time), trip["simulation_end"]))
        self._initialize_trip(trip)
        for _ in range(int(target)):
            self._advance_trip(trip, 1.0)
        if target % 1.0:
            self._advance_trip(trip, target % 1.0)
        trip["current_simulation_time"] = target
        trip["status"] = "REPLAY"
        trip["phase"] = "REPLAY"
        trip["replay_mode"] = True

    def _snapshot(self, trip: Dict[str, Any]) -> Dict[str, Any]:
        model = self.models[trip["id"]]
        trajectories = [model["iceberg"].trajectory(item, trip["current_simulation_time"]) for item in model["initial_icebergs"]]
        state = {"simulation_time": float(trip["current_simulation_time"]), "vessel_state": deepcopy(trip["vessel_state"]), "environment_summary": deepcopy(trip["environment"]), "sea_ice_state": deepcopy(trip["sea_ice"]), "iceberg_states": deepcopy(trip["iceberg_states"]), "iceberg_trajectories": trajectories, "routes": deepcopy(trip["routes"]), "active_route": trip["active_route"], "route_change": deepcopy(trip["route_change"]), "risk": deepcopy(trip["risk"]), "events": deepcopy(trip["events"]), "status": trip["status"], "phase": trip["phase"], "distance_km": trip["distance_km"], "fuel_remaining": trip["fuel_remaining"], "duration_hours": trip["duration_hours"], "risk_score": trip["risk"].get("overall_navigation_risk", 0.0), "trip_id": trip["id"]}
        return state

    @staticmethod
    def _phase_for_time(time: float, trip: Dict[str, Any]) -> str:
        if time >= trip["simulation_end"]:
            return "ARRIVED"
        if time >= trip["simulation_end"] / 2.0:
            return "RETURN"
        return "OUTBOUND"

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> datetime:
        if value is None:
            return datetime.now(timezone.utc).replace(microsecond=0)
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    @staticmethod
    def _record_event(trip: Dict[str, Any], event_type: str, severity: str, title: str, description: str, reason: str, related_objects: Dict[str, Any]) -> None:
        trip["events"].append({"timestamp": float(trip["current_simulation_time"]), "event_type": event_type, "severity": severity, "title": title, "description": description, "reason": reason, "related_objects": related_objects})
