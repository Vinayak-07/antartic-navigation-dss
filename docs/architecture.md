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

- Baseline ML architecture is planned.
- Input features include concentration, drift, and local environmental variables.
- Output includes confidence and uncertainty.

### Iceberg trajectory

- Physics-based model uses wind, current, Coriolis term, mass, geometry, and drag.
- State representation uses [x, y, u, v].
- Numerical integration uses RK45 via scipy.integrate.solve_ivp in the future implementation.

### Risk grid and routing

- Sea-ice and iceberg predictions feed a risk grid.
- Route optimization uses distance, time, fuel, sea-ice risk, iceberg risk, and weather risk.
- Dangerous areas can be excluded as hard constraints.

### Dashboard

- The frontend consumes API endpoints instead of direct module imports.
- The dashboard is designed for both mock and real data without redesign.

## Current status

- TODO: Replace mock data with real dataset adapters.
- TODO: Implement ML prediction baseline.
- TODO: Implement physics-based iceberg motion.
- TODO: Implement route search and decision support scoring.
- PLACEHOLDER: Dashboard is intentionally static and not yet connected to full backend logic.
