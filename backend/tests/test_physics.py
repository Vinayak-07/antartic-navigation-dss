"""Tests for physics module stubs.

TODO: Add actual numerical tests after implementation.
"""


def test_physics_placeholder():
    assert True


class ConstantEnvironment:
    def __init__(self, wind_u=0.0, wind_v=0.0, current_u=0.0, current_v=0.0):
        self.wind_u = wind_u
        self.wind_v = wind_v
        self.current_u = current_u
        self.current_v = current_v

    def at(self, latitude, longitude, simulation_hours):
        return {
            "wind_u_m_s": self.wind_u,
            "wind_v_m_s": self.wind_v,
            "surface_current_u_m_s": self.current_u,
            "surface_current_v_m_s": self.current_v,
        }


def geometry_forcing(environment, state=(0.0, 0.0, 0.0, 0.0), latitude=-65.0):
    from backend.physics.forces import force_diagnostics
    from backend.physics.geometry import compute_geometry

    geometry = compute_geometry(100.0, 40.0, 20.0)
    return force_diagnostics(
        0.0,
        state,
        latitude,
        environment,
        20.0,
        geometry["air_projected_area_m2"],
        geometry["mass_kg"],
        geometry["underwater_projected_area_m2"],
    )


def test_zero_wind_and_current_have_no_drag_force():
    diagnostics = geometry_forcing(ConstantEnvironment())
    assert diagnostics["wind_force_x"] == 0.0
    assert diagnostics["wind_force_y"] == 0.0
    assert diagnostics["water_force_x"] == 0.0
    assert diagnostics["water_force_y"] == 0.0


def test_current_drag_uses_water_relative_velocity_and_strength():
    weak = geometry_forcing(ConstantEnvironment(current_u=1.0))
    strong = geometry_forcing(ConstantEnvironment(current_u=2.0))
    assert weak["water_force_x"] > 0.0
    assert strong["water_force_x"] > weak["water_force_x"]
    assert strong["relative_water_speed"] > weak["relative_water_speed"]


def test_wind_drag_uses_relative_air_velocity_and_strength():
    weak = geometry_forcing(ConstantEnvironment(wind_u=4.0))
    strong = geometry_forcing(ConstantEnvironment(wind_u=8.0))
    assert weak["wind_force_x"] > 0.0
    assert strong["wind_force_x"] > weak["wind_force_x"]
    assert strong["relative_wind_speed"] > weak["relative_wind_speed"]


def test_geometry_changes_mass_and_projected_areas():
    from backend.physics.geometry import compute_geometry

    small = compute_geometry(100.0, 40.0, 20.0)
    large = compute_geometry(120.0, 50.0, 25.0)
    assert large["mass_kg"] > small["mass_kg"]
    assert large["air_projected_area_m2"] > small["air_projected_area_m2"]
    assert large["underwater_projected_area_m2"] > small["underwater_projected_area_m2"]


def test_southern_hemisphere_coriolis_sign_is_consistent():
    from backend.physics.coriolis import coriolis_parameter

    assert coriolis_parameter(-65.0) < 0.0
    assert coriolis_parameter(-65.0) == -coriolis_parameter(65.0)
    diagnostics = geometry_forcing(ConstantEnvironment(), state=(0.0, 0.0, 4.0, 0.0))
    assert diagnostics["coriolis_acceleration_y"] > 0.0


def test_force_diagnostics_are_finite_and_expose_acceleration_terms():
    import math

    diagnostics = geometry_forcing(ConstantEnvironment(wind_u=8.0, current_v=1.5), state=(0.0, 0.0, 1.0, -0.5))
    required = ("wind_force_x", "water_force_y", "coriolis_acceleration_x", "net_acceleration_y", "iceberg_speed", "iceberg_heading")
    assert all(name in diagnostics for name in required)
    assert all(math.isfinite(value) for value in diagnostics.values() if isinstance(value, (int, float)))


def test_controlled_wind_current_trajectories_are_distinct():
    from scipy.integrate import solve_ivp
    from backend.physics.forces import compute_forces
    from backend.physics.geometry import compute_geometry

    geometry = compute_geometry(100.0, 40.0, 20.0)

    def integrate(environment):
        def derivative(time_seconds, state):
            return compute_forces(
                time_seconds,
                state,
                -65.0,
                environment,
                20.0,
                geometry["air_projected_area_m2"],
                geometry["mass_kg"],
                geometry["underwater_projected_area_m2"],
            )

        result = solve_ivp(derivative, (0.0, 6.0 * 3600.0), [0.0, 0.0, 0.0, 0.0], method="RK45", max_step=1800.0)
        return result.y[:, -1]

    calm = integrate(ConstantEnvironment())
    wind = integrate(ConstantEnvironment(wind_u=8.0))
    current = integrate(ConstantEnvironment(current_u=1.5))
    combined = integrate(ConstantEnvironment(wind_u=8.0, current_u=1.5))
    assert calm.tolist() != wind.tolist()
    assert calm.tolist() != current.tolist()
    assert wind.tolist() != combined.tolist()
