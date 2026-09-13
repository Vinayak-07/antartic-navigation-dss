# Physics model overview

## Purpose

This module is responsible for iceberg motion under environmental forcing.

## Implemented synthetic model components

- wind drag
- ocean-current drag
- Coriolis force
- mass and geometry effects
- projected air area and water area
- draft and freeboard
- added mass effects

## State representation

[x, y, u, v]

Where x and y are positions, and u and v are velocity components.

## Numerical method

- `scipy.integrate.solve_ivp` with RK45 integrates the state `[x, y, u, v]`.
- Wind drag, water drag, current forcing, geometry, mass, and latitude-dependent Coriolis acceleration are included.
- Seeded trajectories are cached and interpolated for replay requests.

## Force equations

Wind and water are represented as east/north vectors. For iceberg velocity
`v`, wind vector `w`, and current vector `c`:

```text
v_air   = w - v
v_water = c - v
F_air   = 0.5 * rho_air * Cd_air * A_air * |v_air|   * v_air
F_water = 0.5 * rho_water * Cd_water * A_water * |v_water| * v_water
a_cor   = (f * v_north, -f * v_east)
f       = 2 * Omega * sin(latitude)
a_total = F_air / m_effective + F_water / m_effective + a_cor
```

The effective mass is `iceberg_mass * 1.15`, representing a configurable
added-water-mass approximation. Air projected area and underwater projected
area are derived independently from iceberg dimensions.

## Scope

This is a synthetic scientific simulation prototype. It is deterministic for a given seed, scenario, and model version, and it does not represent real Antarctic observations.
