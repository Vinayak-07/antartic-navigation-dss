# Architecture overview

## Project goal

The project produces three primary outputs:

1. Sea-ice prediction
2. Iceberg trajectory prediction
3. Navigation route optimization

## Core data flow

Data -> Preprocessing -> Environmental features -> Sea-ice model -> Iceberg physics -> Risk grid -> Route optimization -> Decision support -> Dashboard

## Module boundaries

### Environmental data services

- Data loaders are isolated from model code.
- Environmental conditions include sea ice, weather, and ocean state.
- Mock JSON follows the same schema that real scientific datasets will use later.

### Sea-ice prediction

- Baseline machine learning architecture is planned; `backend/prediction/sea_ice_prediction.py` exposes the interface the simulation calls and currently returns a planned-status placeholder.
- Input features will include concentration, drift, and local environmental variables.
- Output will include confidence and uncertainty (`backend/prediction/uncertainty.py`, also a placeholder for now).

### Iceberg trajectory

- Physics-based model uses wind, current, Coriolis term, mass, geometry, and drag (`backend/physics/forces.py`, `coriolis.py`, `geometry.py`).
- State representation uses [x, y, u, v].
- Numerical integration uses RK45 via scipy.integrate.solve_ivp, implemented in `backend/physics/iceberg_dynamics.py`.

### Risk grid and routing

- Sea-ice and iceberg predictions feed a risk grid (`backend/routing/cost_grid.py`).
- Route search uses A* graph search over that grid (`backend/routing/astar.py`), with hard constraints and margin handling in `backend/routing/constraints.py`.
- Route optimization uses distance, time, fuel, sea-ice risk, iceberg risk, and weather risk (`backend/routing/route_scoring.py`, `fuel_estimation.py`).
- Dangerous areas can be excluded as hard constraints.

### Environmental services

- Wind forecast fields (U/V grids) are fetched, cached, and served with staleness metadata by `backend/wind.py`.

### Dashboard

- The frontend consumes API endpoints instead of direct module imports.
- The dashboard is designed for both mock and real data without redesign.
- Map rendering (Leaflet) shows the sea-ice concentration heatmap, iceberg glyphs with RK45 trajectory forecasts, route alternatives, risk zones, the vessel marker, and a wind particle layer.

## Current status

Implemented:

- Physics-based iceberg motion: RK45 trajectory integration over wind, current, Coriolis, and drag in `backend/physics/`.
- Route search and decision-support scoring: A* over the risk/cost grid with multi-factor route scoring in `backend/routing/`.
- Wind field service with caching and staleness tracking (`backend/wind.py`).
- Simulation and trip engines with deterministic state, served over the API surface (`backend/simulation.py`, `backend/app.py`, `backend/api/`).
- Interactive Leaflet dashboard connected to the API: sea-ice heatmap, iceberg trajectories, route alternatives, risk zones, wind particles, voyage playback.

Remaining:

- TODO: Replace mock data with real dataset adapters.
- TODO: Implement the sea-ice prediction baseline (module interface exists, model body still planned).
- TODO: Implement uncertainty estimation for prediction outputs (placeholder).
