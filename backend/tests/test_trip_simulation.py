from backend.simulation import TripEngine


def test_create_trip_sets_unique_id_and_seed():
    engine = TripEngine()
    trip_a = engine.create_trip(vessel="RV Aurora", origin="Cape Town", destination="Bharati Station", scenario="NORMAL")
    trip_b = engine.create_trip(vessel="RV Aurora", origin="Cape Town", destination="Bharati Station", scenario="NORMAL")

    assert trip_a["id"] != trip_b["id"]
    assert trip_a["seed"] != trip_b["seed"]
    assert trip_a["status"] == "NEW"
    assert trip_a["phase"] == "READY"


def test_same_seed_reproduces_scenario():
    engine = TripEngine()
    trip_a = engine.create_trip(vessel="RV Aurora", origin="Cape Town", destination="Bharati Station", scenario="HEAVY_ICE", seed=321)
    trip_b = engine.create_trip(vessel="RV Aurora", origin="Cape Town", destination="Bharati Station", scenario="HEAVY_ICE", seed=321)

    assert trip_a["seed"] == trip_b["seed"]
    assert trip_a["scenario"] == trip_b["scenario"]
    assert trip_a["timeline"][0]["simulation_time"] == trip_b["timeline"][0]["simulation_time"]


def test_step_advances_simulation_clock():
    engine = TripEngine()
    trip = engine.create_trip(vessel="RV Aurora", origin="Cape Town", destination="Bharati Station", scenario="NORMAL", seed=123)
    before = trip["current_simulation_time"]
    engine.start_trip(trip["id"])
    engine.step_trip(trip["id"], steps=1)
    current = engine.get_trip(trip["id"])["current_simulation_time"]
    assert current > before


def test_pause_freezes_simulation():
    engine = TripEngine()
    trip = engine.create_trip(vessel="RV Aurora", origin="Cape Town", destination="Bharati Station", scenario="NORMAL", seed=456)
    engine.start_trip(trip["id"])
    engine.pause_trip(trip["id"])
    current = engine.get_trip(trip["id"])
    assert current["status"] == "PAUSED"
    assert current["phase"] in {"READY", "RUNNING", "REPLAY"}
