---
name: project-audit
description: Complete audit of existing Antarctic Navigation DSS project structure and capabilities
metadata:
  type: project
---

## Project Audit - Antarctic Navigation DSS (SIH 2026)

### Existing Backend Architecture (WORKING)

**Core Modules:**
1. **TripEngine** (`backend/simulation.py`) - In-memory lifecycle manager for deterministic voyage simulations
   - Creates trips with unique IDs and seeds
   - Manages simulation clock (play/pause/reset/step/seek/speed)
   - Tracks vessel state, environment, sea ice, icebergs, routes, events, timeline
   - Deterministic replay via seed-based reconstruction

2. **SyntheticEnvironmentProvider** (`backend/scientific.py`) - Deterministic environmental fields
   - Wind (speed, direction, vectors), Current (speed, direction, vectors), SST, Pressure, Waves
   - Spatially/temporally correlated via seeded noise functions
   - Scenario parameters: NORMAL, HEAVY_ICE, ICEBERG_ENCOUNTER, SEVERE_WEATHER

3. **SeaIceModel** (`backend/scientific.py`) - Sea-ice concentration/thickness/category
   - Categories: Open Water, Low, Moderate, High, Very High
   - Evolves with simulation time
   - Grid generation for visualization

4. **IcebergModel** (`backend/scientific.py`) - RK45 physics integration
   - Forces: wind drag, water drag, Coriolis
   - Geometry: mass, projected areas, effective mass, draft
   - States: DRIFTING, COASTAL, GROUNDED
   - Land constraints via SyntheticAntarcticMask (Shapely)
   - Forecast trajectories at +6h, +12h, +24h, +48h, +72h

5. **Routing** (`backend/routing/`) - A* on cost grid
   - `cost_grid.py`: Dynamic risk-based cost grid (sea-ice + iceberg + weather risk)
   - `astar.py`: A* search with blocked cells (risk > 0.92)
   - `route_scoring.py`: Scores routes on distance, duration, fuel, risk
   - Three reference routes: shortest, optimized, conservative (round-trip)

6. **Risk Model** (`backend/scientific.py::risk_at`) - Composite risk
   - sea_ice_risk, iceberg_risk, weather_risk → overall_navigation_risk
   - Thresholds: LOW (<0.45), WATCH (0.45-0.7), HIGH (>=0.7)

7. **Trip API** (`backend/api/trips.py`) - Full REST endpoints
   - POST /trips, GET /trips, GET /trips/{id}
   - POST /trips/{id}/start|pause|reset|step|seek|speed
   - GET /trips/{id}/state|timeline|events
   - POST /trips/{id}/branch (create continuation from point)

### Existing Frontend Architecture (WORKING)

1. **Leaflet Map** (`frontend/js/map.js`) - Satellite imagery base
   - Route layers (3 styles: dashed yellow, solid green, dashed blue)
   - Iceberg markers with risk circles, trajectories, forecast labels
   - Sea-ice rectangles (grid cells colored by concentration)
   - Vessel marker with heading rotation
   - Layer control panel

2. **Trip Controls** (`frontend/js/trips.js`) - Full simulation control
   - Create trip form (vessel, origin, destination, scenario, departure, seed)
   - Play/Pause/Reset/Step/Seek/Speed controls
   - Timeline slider with event markers
   - Trip history panel

3. **Side Panels** (`frontend/index.html` + `trips.js`)
   - Voyage state (position, speed, heading, fuel, risk, phase)
   - Environmental conditions (wind, current, SST, waves)
   - Sea-ice forecast (concentration, risk, horizon, confidence)
   - Iceberg trajectory details (physics diagnostics, forecast table)
   - Route analysis (distance, time, fuel, safety score, comparison)
   - Event timeline (clickable events with severity)

4. **Styling** (`frontend/css/style.css` + `map.css`)
   - Dark scientific theme with cyan/amber/green/red accents
   - Responsive grid layout
   - Custom Leaflet styling

### Tests (PASSING)
- `test_trip_simulation.py`: Trip lifecycle, determinism, stepping, pausing
- `test_physics.py`: Force diagnostics, Coriolis, geometry, trajectories
- `test_land_constraints.py`: Ocean/land classification, grounding, coastal status
- `test_scientific_simulation.py`: Environment, sea ice, icebergs, routing, risk, replay

### Gaps vs CLAUDE.md Requirements

| Phase | Requirement | Status |
|-------|-------------|--------|
| 7 | Continuous sea-ice visualization (interpolation, smooth surfaces) | ❌ Rectangular grid cells only |
| 10 | Wind animation (particles/streamlines) | ❌ Not implemented |
| 11 | Current animation | ❌ Not implemented |
| 12 | Wave visualization | ❌ Not implemented |
| 13 | Smooth iceberg animation (interpolation) | ❌ Discrete updates only |
| 5 | Vessel dynamics (smooth heading, acceleration, turn rate) | ❌ Teleports between points |
| 19 | Explain mode (normal vs technical) | ❌ Not implemented |
| 18 | Event story engine (structured narrative) | ⚠️ Basic events exist |
| 20 | Voyage playback (video-like controls) | ⚠️ Basic controls exist |
| 30 | Advanced map layers (toggleable) | ⚠️ Layer control exists |
| 34 | Visual storytelling mode | ❌ Not implemented |
| 36 | Technical inspection mode | ⚠️ Partial (iceberg popup) |
| 37 | Deterministic replay (seek reconstructs state) | ⚠️ Re-runs from start |
| 61 | Visual interpolation (backend discrete, frontend smooth) | ❌ Not implemented |
| 72 | Layered explanations (short + technical) | ⚠️ Partial |

### Critical Architecture Notes
- Backend is the **source of truth** for all scientific computation
- Frontend only visualizes - NO scientific logic in JavaScript (GOOD)
- Deterministic replay via seed + simulation time works
- RK45 iceberg physics preserved and tested
- Land constraints enforced for icebergs and routes
- Event system exists with timestamps, types, severity, related objects
- Three reference routes + actual vessel route concept exists

### Next Steps Priority
1. **Phase 7**: Continuous sea-ice visualization (frontend interpolation)
2. **Phase 5**: Vessel dynamics (smooth movement, heading, acceleration)
3. **Phase 10-12**: Environmental animations (wind, current, waves)
4. **Phase 13**: Smooth iceberg animation
5. **Phase 14**: Physics visualization mode (enhance existing)
6. **Phase 19**: Explain mode (normal/technical toggle)
7. **Phase 18**: Event story engine enhancement
8. **Phase 34**: Visual storytelling mode