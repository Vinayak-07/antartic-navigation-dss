from backend.routing.astar import find_route
from backend.scientific import IcebergModel, SeaIceModel, SyntheticEnvironmentProvider, build_routes, iceberg_route_risk, risk_at
from backend.simulation import TripEngine


def test_environment_is_deterministic_and_correlated():
    first = SyntheticEnvironmentProvider(101, "NORMAL").at(-58.0, 28.0, 12.0)
    second = SyntheticEnvironmentProvider(101, "NORMAL").at(-58.0, 28.0, 12.0)
    changed = SyntheticEnvironmentProvider(101, "SEVERE_WEATHER").at(-58.0, 28.0, 12.0)
    assert first == second
    assert first["wind_speed_m_s"] != changed["wind_speed_m_s"]
    assert first["wind_speed_m_s"] > first["ocean_current_speed_m_s"]


def test_sea_ice_bounds_categories_and_time_evolution():
    model = SeaIceModel(SyntheticEnvironmentProvider(202, "HEAVY_ICE"))
    early = model.grid(0.0)
    later = model.grid(72.0)
    assert all(0.0 <= cell["concentration"] <= 1.0 for cell in early)
    assert all(cell["category"] in {"Open Water", "Low", "Moderate", "High", "Very High"} for cell in early)
    assert early != later
    assert all(cell["thickness_m"] >= 0.05 for cell in later)


def test_seeded_icebergs_have_geometry_and_move_with_rk45():
    environment = SyntheticEnvironmentProvider(303, "NORMAL")
    model = IcebergModel(303, "NORMAL", environment)
    icebergs = model.generate([[-34.0, 18.0], [-69.0, 76.0]], 5)
    before = model.state_at(icebergs[0], 0.0)
    after = model.state_at(icebergs[0], 24.0)
    trajectory = model.trajectory(icebergs[0], 0.0)
    assert len({item["id"] for item in icebergs}) == 5
    assert before["estimated_mass_kg"] > 0
    assert (before["lat"], before["lon"]) != (after["lat"], after["lon"])
    assert trajectory["geometry"]["type"] == "LineString"
    assert len(trajectory["geometry"]["coordinates"]) == 6


def test_trip_vessel_fuel_risk_rerouting_and_replay():
    engine = TripEngine()
    trip = engine.create_trip("RV Aurora", "Cape Town", "Bharati Station", "ICEBERG_ENCOUNTER", seed=404)
    engine.start_trip(trip["id"])
    for _ in range(25):
        engine.step_trip(trip["id"])
    state = engine.get_trip_state(trip["id"])
    assert state["distance_km"] > 0
    assert state["vessel_state"]["fuel_remaining_pct"] < 100
    assert set(("sea_ice_risk", "iceberg_risk", "weather_risk", "overall_navigation_risk")) <= set(state["risk"])
    assert state["active_route"] in {"optimized", "conservative"}
    assert any(event["event_type"] == "ROUTE_RECALCULATED" for event in state["events"])
    engine.seek_trip(trip["id"], 5)
    replay = engine.get_trip_state(trip["id"])
    assert replay["status"] == "REPLAY"
    assert replay["simulation_time"] == 5
    assert replay["vessel_state"]["lat"] != state["vessel_state"]["lat"]


def test_round_trip_phase_and_reproducibility():
    first = TripEngine()
    second = TripEngine()
    trip_a = first.create_trip("RV Aurora", "Cape Town", "Maitri Station", "NORMAL", seed=505)
    trip_b = second.create_trip("RV Aurora", "Cape Town", "Maitri Station", "NORMAL", seed=505)
    assert trip_a["iceberg_states"] == trip_b["iceberg_states"]
    assert trip_a["sea_ice"] == trip_b["sea_ice"]
    first.start_trip(trip_a["id"])
    for _ in range(121):
        first.step_trip(trip_a["id"])
    assert first.get_trip(trip_a["id"])["phase"] == "RETURN"


def test_route_optimizer_and_blocked_cell_search():
    engine = TripEngine()
    trip = engine.create_trip("RV Aurora", "Cape Town", "Bharati Station", "HEAVY_ICE", seed=606)
    assert trip["routes"]["optimized"]["distance_km"] > 0
    assert trip["routes"]["optimized"]["safety_score"] >= 0.0
    blocked_grid = {
        "step": 1.0,
        "cells": {
            (0.0, 0.0): {"blocked": False, "cost": 1.0, "risk": {"overall_navigation_risk": 0.1}},
            (0.0, 1.0): {"blocked": True, "cost": 1.0, "risk": {"overall_navigation_risk": 1.0}},
            (0.0, 2.0): {"blocked": False, "cost": 1.0, "risk": {"overall_navigation_risk": 0.1}},
            (1.0, 0.0): {"blocked": False, "cost": 1.0, "risk": {"overall_navigation_risk": 0.1}},
            (1.0, 1.0): {"blocked": False, "cost": 1.0, "risk": {"overall_navigation_risk": 0.1}},
            (1.0, 2.0): {"blocked": False, "cost": 1.0, "risk": {"overall_navigation_risk": 0.1}},
        },
    }
    route = find_route(blocked_grid, [0.0, 0.0], [0.0, 2.0])
    assert [0.0, 1.0] not in route


def test_route_risk_increases_when_predicted_iceberg_approaches_route():
    route = [[-60.0, 20.0], [-61.0, 21.0], [-62.0, 22.0]]
    iceberg = {"id": "IB-TEST", "lat": -60.0, "lon": 20.0, "length_m": 300.0, "risk_radius_m": 50000.0}
    near = {"type": "Feature", "geometry": {"coordinates": [[20.0, -60.0], [20.5, -60.5]]}, "properties": {"horizons_hours": [6]}}
    far = {"type": "Feature", "geometry": {"coordinates": [[35.0, -45.0], [36.0, -44.0]]}, "properties": {"horizons_hours": [6]}}
    near_risk = iceberg_route_risk(iceberg, route, near)
    far_iceberg = {**iceberg, "lat": -45.0, "lon": 35.0}
    far_risk = iceberg_route_risk(far_iceberg, route, far)
    assert near_risk["risk_score"] > far_risk["risk_score"]
    assert near_risk["route_conflict"] is True
    assert far_risk["route_conflict"] is False


def test_trip_state_contains_diagnostics_horizons_and_replay_is_repeatable():
    first = TripEngine()
    trip = first.create_trip("RV Aurora", "Cape Town", "Bharati Station", "NORMAL", seed=707)
    state = first.get_trip_state(trip["id"])
    iceberg = state["iceberg_states"][0]
    diagnostics = iceberg["physics_diagnostics"]
    assert {"wind_force_x", "water_force_x", "net_acceleration_x"} <= set(diagnostics)
    assert state["iceberg_trajectories"][0]["properties"]["horizons_hours"] == [6, 12, 24, 48, 72]
    first.seek_trip(trip["id"], 12)
    replay_one = first.get_trip_state(trip["id"])
    second = TripEngine()
    trip_copy = second.create_trip("RV Aurora", "Cape Town", "Bharati Station", "NORMAL", seed=707)
    second.seek_trip(trip_copy["id"], 12)
    replay_two = second.get_trip_state(trip_copy["id"])
    assert replay_one["iceberg_states"] == replay_two["iceberg_states"]
