# Antarctic Sea-Ice, Iceberg Trajectory and Navigation Decision Support System

## Project overview

This project is a deterministic Antarctic voyage simulation prototype focused on:

1. Sea-ice prediction
2. Iceberg trajectory prediction
3. Navigation route optimization

The active trip engine combines a time-varying synthetic environment, sea-ice
field, RK45 iceberg trajectories with coastal protection, route alternatives,
risk assessment, vessel playback, and an interactive Leaflet map. It is a
scientific demonstration, not an operational navigation system.

## Current status

- Deterministic trip creation, playback, seeking, replay, and event history.
- RK45 iceberg drift and a synthetic Antarctic land/coast constraint.
- Route alternatives and risk-informed rerouting.
- Continuous interpolated sea-ice surface on the map.
- Open-Meteo-derived U/V wind forecast particle layer with caching and
  provenance. See `docs/wind_layer.md`.

## High-level architecture

Environment -> sea ice -> iceberg physics -> risk -> route optimization -> vessel
motion -> trip state -> map

## Operational scenario

- Origin: Cape Town, South Africa
- Destinations: Bharati Station and Maitri Station
- Vessel, departure time, and forecast horizon are selected in the dashboard.
- The system is a navigation decision support tool for human operators, not an autonomous navigation system.

## Strict project rule

The design is based on physics-based modelling, numerical methods, geospatial
computation, scientific datasets, graph algorithms, optimization, and
statistical methods.

## Folder layout

See the project tree for the initial structure.

## API endpoints

- GET /api/health
- POST /api/voyage/analyze
- GET /api/sea-ice
- GET /api/icebergs
- POST /api/icebergs/predict
- POST /api/routes/optimize
- GET /api/environment
- GET /api/wind
- POST /api/trips and trip-state/playback endpoints

## Requirements

Please see requirements.txt for the Python dependencies.

## Notes

Legacy single-purpose API modules remain for compatibility; an active trip's
state is the source of truth for the map and simulation controls.
