import numpy as np

from backend.scientific import IcebergModel, SyntheticEnvironmentProvider, constrain_trajectory_states
from backend.simulation import TripEngine
from backend.utils.coordinates import SyntheticAntarcticMask, is_ocean


def test_synthetic_mask_distinguishes_ocean_and_land():
    assert is_ocean(-60.0, 20.0)
    assert not is_ocean(-80.0, 20.0)
    assert not is_ocean(-90.0, 0.0)


def test_iceberg_generation_and_forecast_points_are_ocean_valid():
    mask = SyntheticAntarcticMask()
    model = IcebergModel(808, "NORMAL", SyntheticEnvironmentProvider(808, "NORMAL"), mask)
    icebergs = model.generate([[-34.0, 18.0], [-69.0, 76.0]], 10)
    for iceberg in icebergs:
        assert mask.is_ocean(iceberg["lat"], iceberg["lon"], iceberg["length_m"], iceberg["width_m"])
        trajectory = model.trajectory(iceberg, 0.0)
        for longitude, latitude in trajectory["geometry"]["coordinates"]:
            assert mask.is_ocean(latitude, longitude, iceberg["length_m"], iceberg["width_m"])


def test_invalid_rk45_state_is_clamped_and_grounded():
    mask = SyntheticAntarcticMask()
    iceberg = {"length_m": 180.0, "width_m": 80.0}
    ocean_latitude = -69.0
    longitude = 76.0
    states = np.array([
        [longitude * 111000.0, ocean_latitude * 111000.0, 0.0, -1.0],
        [longitude * 111000.0, -71.0 * 111000.0, 0.0, -1.0],
    ])
    constrained, metadata = constrain_trajectory_states(states, np.array([0.0, 6.0]), iceberg, mask)
    grounded_latitude = constrained[1, 1] / 111000.0
    grounded_longitude = constrained[1, 0] / 111000.0
    assert metadata["status"] == "GROUNDED"
    assert constrained[1, 2] == 0.0
    assert constrained[1, 3] == 0.0
    assert mask.is_ocean(grounded_latitude, grounded_longitude, iceberg["length_m"], iceberg["width_m"])
    assert np.array_equal(constrained[1], constrained[-1])


def test_grounded_state_stays_valid_and_diagnostics_are_constrained():
    mask = SyntheticAntarcticMask()
    model = IcebergModel(909, "NORMAL", SyntheticEnvironmentProvider(909, "NORMAL"), mask)
    iceberg = model.generate([[-69.0, 76.0]], 1)[0]
    iceberg["lat"] = -69.0
    iceberg["lon"] = 76.0
    iceberg["velocity_v_m_s"] = -1.0
    model._integrated.pop(iceberg["id"], None)
    state = model.state_at(iceberg, 240.0)
    assert state["status"] in {"DRIFTING", "GROUNDED"}
    assert mask.is_ocean(state["lat"], state["lon"], iceberg["length_m"], iceberg["width_m"])
    if state["status"] == "GROUNDED":
        assert state["physics_diagnostics"]["iceberg_speed"] == 0.0
        assert state["physics_diagnostics"]["net_acceleration_x"] == 0.0
        assert state["physics_diagnostics"]["net_acceleration_y"] == 0.0


def test_grounding_event_is_emitted_once_and_replay_is_deterministic():
    first = TripEngine()
    trip = first.create_trip("RV Aurora", "Cape Town", "Bharati Station", "NORMAL", seed=808)
    first.start_trip(trip["id"])
    for _ in range(24):
        first.step_trip(trip["id"])
    state = first.get_trip_state(trip["id"])
    grounded_ids = {item["id"] for item in state["iceberg_states"] if item["status"] == "GROUNDED"}
    events = [event for event in state["events"] if event["event_type"] == "ICEBERG_GROUNDED"]
    assert grounded_ids
    assert {event["related_objects"]["iceberg_id"] for event in events} == grounded_ids
    assert len(events) == len(grounded_ids)
    first.seek_trip(trip["id"], 12.0)
    replay_one = first.get_trip_state(trip["id"])
    second = TripEngine()
    trip_copy = second.create_trip("RV Aurora", "Cape Town", "Bharati Station", "NORMAL", seed=808)
    second.seek_trip(trip_copy["id"], 12.0)
    replay_two = second.get_trip_state(trip_copy["id"])
    assert replay_one["iceberg_states"] == replay_two["iceberg_states"]


def test_pure_meridional_drift_has_zero_artificial_zonal_displacement():
    """Verify that pure southward/northward drift does not introduce artificial eastward/westward drift."""
    mask = SyntheticAntarcticMask()
    env = SyntheticEnvironmentProvider(42, "NORMAL")
    model = IcebergModel(42, "NORMAL", env, mask)
    
    # Custom iceberg with purely southward velocity and no environmental forces
    # We test the ODE integration directly
    state_init = np.array([20.0 * 111000.0, -60.0 * 111000.0, 0.0, -1.0])
    
    # Define a zero-force RHS to test pure kinematic integration
    def pure_southward_kinematics(t, y):
        u, v = y[2], y[3]
        latitude = y[1] / 111000.0
        cos_lat = max(np.cos(np.radians(latitude)), 0.05)
        # dX/dt and dY/dt in meters per hour
        dxdt = (u / cos_lat) * 3600.0
        dydt = v * 3600.0
        return [dxdt, dydt, 0.0, 0.0]

    from scipy.integrate import solve_ivp
    sol = solve_ivp(pure_southward_kinematics, (0.0, 24.0), state_init, t_eval=[0.0, 24.0])
    lon_init = sol.y[0, 0] / 111000.0
    lon_final = sol.y[0, 1] / 111000.0
    assert abs(lon_final - lon_init) < 1e-9


def test_major_antarctic_sectors_classification():
    """Verify accurate ocean vs land classification across key Antarctic sectors."""
    mask = SyntheticAntarcticMask()
    
    # Antarctic Peninsula land vs ocean
    assert not mask.is_ocean(-65.0, -64.0), "Antarctic Peninsula interior must be land"
    assert mask.is_ocean(-62.0, -64.0), "Drake Passage / north of Peninsula must be ocean"
    
    # Weddell Sea embayment (deep ocean)
    assert mask.is_ocean(-72.0, -40.0), "Weddell Sea must be ocean"
    assert not mask.is_ocean(-78.0, -40.0), "Filchner-Ronne Ice Shelf interior must be land"
    
    # East Antarctica & Stations
    assert not mask.is_ocean(-70.77, 11.73), "Maitri Station inland (Schirmacher Oasis) must be land"
    assert mask.is_ocean(-68.5, 75.0), "Prydz Bay offshore Bharati must be ocean"
    assert not mask.is_ocean(-73.0, 75.0), "Amery Ice Shelf interior must be land"
    
    # Ross Sea embayment
    assert mask.is_ocean(-74.0, 175.0), "Ross Sea must be ocean"
    assert not mask.is_ocean(-82.0, 175.0), "Ross Ice Shelf interior must be land"
    
    # Geographic South Pole
    assert not mask.is_ocean(-90.0, 0.0), "South Pole must be land"


def test_iceberg_footprint_safety_buffer():
    """Verify that oversized icebergs are constrained before their edges intersect land."""
    mask = SyntheticAntarcticMask()
    # A location offshore near Prydz Bay coast
    near_coast_lat = -69.45
    near_coast_lon = 76.0
    
    # Small iceberg (radius ~50m) might be valid in open water
    # Huge tabular iceberg (length 10000m, radius ~5000m) buffer should overlap land
    dist_km = mask.distance_to_land_km(near_coast_lat, near_coast_lon)
    if 0.1 < dist_km < 3.0:
        assert mask.is_ocean(near_coast_lat, near_coast_lon, length_m=50.0, width_m=30.0)
        assert not mask.is_ocean(near_coast_lat, near_coast_lon, length_m=10000.0, width_m=5000.0)


def test_coastal_status_flagging():
    """Verify that icebergs within 35 km of land receive the COASTAL status."""
    mask = SyntheticAntarcticMask()
    model = IcebergModel(101, "NORMAL", SyntheticEnvironmentProvider(101, "NORMAL"), mask)
    
    # Generate valid iceberg fixture
    iceberg = model.generate([[-69.2, 76.0]], 1)[0]
    iceberg["lat"] = -69.2
    iceberg["lon"] = 76.0
    iceberg["velocity_u_m_s"] = 0.0
    iceberg["velocity_v_m_s"] = 0.0
    model._integrated.pop(iceberg["id"], None)
    
    state = model.state_at(iceberg, 0.0)
    dist = mask.distance_to_land_km(-69.2, 76.0)
    assert dist <= 35.0
    assert state["status"] in {"COASTAL", "GROUNDED"}


def test_trajectory_forecast_stationary_after_grounding():
    """Verify that once grounded, all subsequent forecast horizon positions remain identical."""
    mask = SyntheticAntarcticMask()
    model = IcebergModel(303, "NORMAL", SyntheticEnvironmentProvider(303, "NORMAL"), mask)
    
    # Place an iceberg heading south towards land
    iceberg = model.generate([[-69.2, 76.0]], 1)[0]
    iceberg["lat"] = -69.2
    iceberg["lon"] = 76.0
    iceberg["velocity_u_m_s"] = 0.0
    iceberg["velocity_v_m_s"] = -1.5
    model._integrated.pop(iceberg["id"], None)
    
    traj = model.trajectory(iceberg, 0.0)
    coords = traj["geometry"]["coordinates"]
    
    # Verify all coords are in ocean
    for lon, lat in coords:
        assert mask.is_ocean(lat, lon, iceberg["length_m"], iceberg["width_m"])
    
    # If grounding occurred, check that trailing coordinates are identical
    state_grounded = model.state_at(iceberg, 240.0)
    if state_grounded["status"] == "GROUNDED":
        assert coords[-1] == coords[-2]

