You are the lead software architect, scientific-simulation engineer, geospatial developer, numerical-modelling engineer, optimization engineer, backend engineer, and frontend visualization engineer working on my existing project:

Project purpose:

This is an SIH 2026 prototype for problem statement 26059 associated with Antarctic sea-ice prediction, iceberg trajectory prediction, and navigation decision support for Indian Antarctic research-vessel operations.

The project must evolve into a realistic, interactive, futuristic, game-like scientific simulation.

The final prototype must allow a normal viewer to understand what is happening visually while allowing a technical evaluator to inspect the underlying mathematical, physical, environmental, predictive, and optimization information.

============================================================
ABSOLUTE PROJECT TERMINOLOGY RULE
============================================================

There is one strict terminology constraint:

DO NOT use the forbidden AI-related term anywhere in the project.

Do not use it in:

- source code
- comments
- variable names
- class names
- function names
- API routes
- frontend text
- backend text
- documentation
- README
- UI labels
- logs
- console messages
- filenames
- tooltips
- event descriptions
- database/table names
- configuration names
- architecture diagrams
- project explanations

Use terminology such as:

- machine learning
- predictive modelling
- physics-based modelling
- numerical modelling
- statistical modelling
- numerical integration
- geospatial computation
- graph algorithms
- mathematical optimization
- scientific simulation
- environmental modelling
- decision support
- trajectory prediction
- risk modelling

Core project philosophy:

"ML predicts.
Physics explains movement.
Optimization chooses the route."

============================================================
IMPORTANT EXISTING PROJECT RULE
============================================================

This is an existing working project.

DO NOT rebuild it from scratch.

DO NOT create a second architecture unnecessarily.

DO NOT delete working systems simply because another implementation appears easier.

DO NOT replace the existing simulation engine with a simplified one.

DO NOT replace RK45 iceberg dynamics with random movement.

DO NOT replace A* with a fake route.

DO NOT implement scientific logic in JavaScript.

DO NOT create decorative numbers that are not connected to backend simulation state.

DO NOT break deterministic replay.

DO NOT remove land/coast protection.

DO NOT remove existing tests.

First inspect everything.

Understand:

- existing backend
- existing frontend
- existing simulation state
- existing route engine
- existing environmental model
- existing sea-ice model
- existing iceberg model
- existing trip engine
- existing APIs
- existing tests
- existing visualization architecture

Then improve incrementally.

============================================================
PYTHON ENVIRONMENT
============================================================

Use the existing project Python environment:

C:\Users\krish\Desktop\antarctic-navigation-dss\ice\Scripts\python.exe

Do not recreate it.

Do not replace it.

Use this interpreter for:

- testing
- backend execution
- scientific calculations
- validation

============================================================
CORE SYSTEM VISION
============================================================

The final system is a dynamic Antarctic voyage simulator.

It should feel like:

scientific simulation
+
interactive map
+
navigation console
+
real-time environmental system
+
route optimization system
+
educational visualization
+
replayable simulation

It must NOT feel like:

- a static dashboard
- a collection of fake cards
- a slideshow
- a static map with random markers
- a frontend animation disconnected from backend science

The user should be able to watch an entire voyage evolve.

============================================================
THE CENTRAL SIMULATION LOOP
============================================================

The entire project is based on this loop:

                    SIMULATION CLOCK
                           ↓
                  ENVIRONMENT MODEL
                 /       |        \
              WIND     CURRENT    WAVES
                 \       |        /
                           ↓
                     SEA-ICE MODEL
                           ↓
                    ICEBERG PHYSICS
                           ↓
                  FUTURE ENVIRONMENT
                           ↓
                  NAVIGATION COST FIELD
                           ↓
                ROUTE OPTIMIZATION ENGINE
                           ↓
                    ACTUAL SHIP PATH
                           ↓
                     SHIP MOTION
                           ↓
                       NEW STATE
                           ↓
                     RISK UPDATE
                           ↓
                  ROUTE RE-EVALUATION
                           ↓
                     SIMULATION LOOP
                           ↺

Every major visual behaviour must originate from this loop.

============================================================
THREE PRIMARY SYSTEM OUTPUTS
============================================================

Everything must support three primary capabilities.

------------------------------------------------------------
1. PREDICT ICE
------------------------------------------------------------

Question:

"How much sea ice will be present and how navigable is the area?"

Predict:

- concentration
- thickness
- category
- navigability
- navigation risk
- temporal evolution

------------------------------------------------------------
2. PREDICT ICEBERGS
------------------------------------------------------------

Question:

"Where will the iceberg move?"

Predict:

- future position
- velocity
- heading
- trajectory
- forecast horizon
- route proximity
- risk

------------------------------------------------------------
3. PREDICT ROUTE
------------------------------------------------------------

Question:

"Where should the vessel travel?"

Calculate:

- reference routes
- actual optimized route
- distance
- ETA
- fuel
- sea-ice risk
- iceberg risk
- environmental risk
- overall navigation risk
- safety score

============================================================
MOST IMPORTANT ROUTE CONCEPT
============================================================

There are FOUR route concepts visible to the user.

1. Reference Route A
2. Reference Route B
3. Reference Route C
4. Actual Vessel Route

The three reference routes are predicted/reference alternatives.

They are NOT hard constraints.

The vessel is NOT required to stay on them.

The actual vessel path is independently generated by the navigation optimizer.

Therefore:

REFERENCE ROUTES
        +
CURRENT ENVIRONMENT
        +
SEA ICE
        +
ICEBERGS
        +
WEATHER
        +
WATER CURRENTS
        +
WAVES
        +
VESSEL CONSTRAINTS
        +
FUEL
        ↓
NAVIGATION COST FIELD
        ↓
ROUTE OPTIMIZATION
        ↓
ACTUAL VESSEL PATH

The vessel must be allowed to leave all three reference paths.

This is a major feature.

The reference routes show what alternative corridor possibilities existed.

The actual vessel route shows what the system currently decided.

============================================================
SIMULATION GEOGRAPHY
============================================================

Primary prototype voyage:

Origin:

Cape Town, South Africa

Destination:

Bharati access region
or
Maitri maritime access/offshore logistics waypoint

Return:

Destination
→
Cape Town

IMPORTANT:

Maitri is inland.

The vessel must not physically navigate to the inland station coordinate.

Use an appropriate coastal/offshore access representation for maritime navigation.

Bharati should be represented using a maritime-access region appropriate to the Larsemann Hills/Prydz Bay context.

The system should clearly communicate that this is a maritime logistics simulation.

============================================================
PHASE 0 — COMPLETE PROJECT AUDIT
============================================================

Before coding:

Inspect the complete repository.

Inspect:

backend/
frontend/
data/
models/
notebooks/
outputs/
docs/
tests/
requirements/
environment/configuration files

Understand every important module.

Create an internal architecture map.

Identify:

- existing working components
- incomplete components
- duplicated components
- hardcoded mock APIs
- scientific logic
- frontend-only logic
- backend-only logic
- state-flow problems
- naming conflicts
- performance bottlenecks
- synchronization problems

Do not modify anything during the initial audit.

Produce an implementation plan before making major changes.

============================================================
PHASE 1 — SCIENTIFIC FOUNDATION
============================================================

Ensure that the backend remains the source of truth.

Scientific systems:

1. environmental model
2. sea-ice model
3. iceberg physics
4. trajectory forecasting
5. risk model
6. route cost model
7. optimization
8. vessel dynamics
9. simulation clock

All must use a common simulation state.

------------------------------------------------------------
1. ENVIRONMENT
------------------------------------------------------------

Provide:

- wind speed
- wind direction
- wind vector
- current speed
- current direction
- current vector
- temperature
- sea-surface temperature
- pressure
- wave height
- wave direction

Environment must vary:

- spatially
- temporally
- smoothly
- deterministically

Do not regenerate unrelated random numbers every frame.

Use correlated fields.

Same:

seed
+
position
+
simulation time

must produce the same result.

------------------------------------------------------------
2. SEA ICE
------------------------------------------------------------

Canonical categories:

OPEN_WATER
VERY_OPEN_ICE
OPEN_ICE
CLOSE_ICE
VERY_CLOSE_ICE
FAST_ICE

Each sea-ice sample should contain:

latitude
longitude
concentration
thickness_m
category
navigability
navigation_risk
risk_score
timestamp

Navigation risk:

LOW
MODERATE
HIGH
EXTREME
BLOCKED

Sea ice must evolve with time.

Maintain:

- smooth spatial variation
- temporal correlation
- realistic bounded concentration
- physically plausible thickness
- deterministic behaviour

FAST_ICE:

Do not classify the entire Antarctic area as FAST_ICE.

Create a deterministic near-coastal/land-connected fast-ice field.

FAST_ICE should persist more strongly than drifting sea ice.

------------------------------------------------------------
3. ICEBERG MODEL
------------------------------------------------------------

Preserve existing RK45 integration.

Forces should include:

- air drag
- water drag
- Coriolis acceleration
- wind forcing
- current forcing

Preserve geometry-dependent quantities:

- mass
- projected area
- submerged dimensions
- effective mass

Maintain:

- DRIFTING
- COASTAL
- GROUNDED

Grounded icebergs:

- must not move through land
- must remain valid
- must not teleport
- must have stationary/limited physically valid behaviour

------------------------------------------------------------
4. LAND CONSTRAINTS
------------------------------------------------------------

Ensure:

- no iceberg through Antarctica
- no route through land
- no ship through land
- no invalid inland maritime route
- no impossible coordinate drift

Perform geometry checks.

Maintain the current improved Antarctic coastal/sector model.

============================================================
PHASE 2 — PREDICTION SYSTEM
============================================================

Create a unified prediction architecture.

------------------------------------------------------------
SEA-ICE FORECAST
------------------------------------------------------------

Support temporal forecasts.

Example:

+6h
+12h
+24h
+48h
+72h

For each forecast:

- concentration
- thickness
- category
- navigability
- risk

------------------------------------------------------------
ICEBERG FORECAST
------------------------------------------------------------

Forecast:

+6h
+12h
+24h
+48h
+72h

Generate actual backend trajectories using the physics model.

Do not generate predicted paths only for visualization.

Predictions must feed risk calculations.

------------------------------------------------------------
ROUTE FORECAST
------------------------------------------------------------

Calculate multiple candidate routes from the environmental cost field.

Keep three reference routes.

Then independently calculate the actual vessel route.

============================================================
PHASE 3 — NAVIGATION COST FIELD
============================================================

Create a unified navigation cost field.

Every cell/point should represent:

distance cost
+
time cost
+
fuel cost
+
sea-ice risk
+
iceberg risk
+
environmental risk
+
vessel constraints

Potential formulation:

C =
w_distance * distance_cost
+
w_time * time_cost
+
w_fuel * fuel_cost
+
w_ice * sea_ice_risk
+
w_iceberg * iceberg_risk
+
w_weather * weather_risk

Weights should be configurable.

Never hide the weights.

The evaluator should be able to inspect them.

============================================================
PHASE 4 — ROUTE OPTIMIZATION
============================================================

Preserve A*.

Improve route optimization so that:

- unsafe cells are blocked
- high-risk cells have increased cost
- sea-ice risk influences path
- iceberg risk influences path
- environment influences path
- fuel influences path
- route geometry is valid

The optimizer should produce:

- path coordinates
- total distance
- expected duration
- expected fuel
- sea-ice risk
- iceberg risk
- environment risk
- overall risk
- safety score

============================================================
PHASE 5 — VESSEL DYNAMICS
============================================================

This phase is critical.

The vessel should move continuously.

Never teleport between route points.

Represent the vessel with:

latitude
longitude
heading
speed
target_speed
acceleration
turn_rate
fuel
fuel_rate
distance_travelled
distance_remaining
ETA
current_route_segment

Implement smooth movement.

Heading should gradually respond to route curvature.

Acceleration should be bounded.

Turn rate should be bounded.

When the optimizer changes the route:

the vessel should not instantly jump.

Instead:

old heading
↓
turn behaviour
↓
new heading
↓
new path

This should be visible.

============================================================
PHASE 6 — SIMULATION CLOCK AND TIME ENGINE
============================================================

Create one authoritative simulation clock.

Support:

PLAY
PAUSE
RESET
STEP FORWARD
STEP BACK
SEEK
REPLAY

Playback speeds:

0.5x
1x
2x
5x
10x
50x

The clock controls:

- environment
- ice
- icebergs
- vessel
- route
- events
- timeline

Seeking must reconstruct deterministic state.

Do not merely move the UI timeline while leaving backend state unchanged.

============================================================
PHASE 7 — CONTINUOUS SEA-ICE VISUALIZATION
============================================================

This is the first major visual transformation.

The sea-ice visualization must look like a continuous environmental field.

Do NOT show:

large obvious grid squares
+
box-by-box colour blocks.

The computational grid may remain internally.

Frontend visualization should use:

- interpolation
- smooth raster-like surfaces
- blurred contours
- continuous gradients
- semi-transparent layers
- dynamic boundaries

The visual density should evolve over time.

Show:

open water
lighter ice
denser ice
very dense ice
fast ice

Navigation risk should be visually encoded carefully.

The map must remain readable.

============================================================
PHASE 8 — FUTURISTIC MAP EXPERIENCE
============================================================

The map is the primary interface.

Do not create a traditional dashboard with dozens of cards.

Use:

FULL-SCREEN MAP
+
FLOATING TELEMETRY
+
CONTEXTUAL INFORMATION
+
ANIMATED ENVIRONMENT

Design language:

- futuristic
- scientific
- premium
- minimal
- dark
- high-information-density
- clean
- elegant
- cinematic

Avoid:

- excessive neon
- random glow
- giant cards everywhere
- generic admin dashboard appearance
- decorative charts with no purpose
- unnecessary 3D effects

Use visual hierarchy.

The map is the hero.

============================================================
PHASE 9 — UNIVERSAL INTERACTION SYSTEM
============================================================

Everything meaningful should be interactive.

Clickable objects:

SHIP
ICEBERG
REFERENCE ROUTE
ACTUAL ROUTE
SEA ICE
WIND
CURRENT
WAVES
RISK ZONE
EVENT
ORIGIN
DESTINATION

Clicking an object should open contextual information.

Do not make the user navigate through unrelated panels.

------------------------------------------------------------
SHIP CLICK
------------------------------------------------------------

Display:

- vessel name
- position
- heading
- speed
- target speed
- fuel
- ETA
- distance travelled
- remaining distance
- current risk
- current route
- current route reason

------------------------------------------------------------
ICEBERG CLICK
------------------------------------------------------------

Display:

- iceberg ID
- position
- velocity
- heading
- dimensions
- mass
- state
- risk
- closest route
- predicted positions
- route conflict status

Also allow technical physics inspection.

------------------------------------------------------------
SEA-ICE CLICK
------------------------------------------------------------

Display:

- concentration
- thickness
- category
- navigability
- risk
- environmental timestamp

------------------------------------------------------------
ROUTE CLICK
------------------------------------------------------------

Display:

- route type
- route status
- distance
- duration
- fuel
- sea-ice risk
- iceberg risk
- environment risk
- safety score

------------------------------------------------------------
ENVIRONMENT CLICK
------------------------------------------------------------

Display:

- wind speed
- wind direction
- current speed
- current direction
- temperature
- pressure
- wave height
- wave direction

============================================================
PHASE 10 — WIND ANIMATION
============================================================

Add animated wind visualization.

The preferred implementation is a Windy.com / earth.nullschool-style
particle-advection layer driven by real model-derived wind data.

Possible visual techniques include:

- particles
- streamlines
- moving vectors
- flowing traces

The production/default implementation for the Leaflet map should use
`leaflet-velocity` unless the existing architecture already contains
an equivalent tested vector-field renderer.

Wind movement must come from an actual U/V vector field supplied by the
backend wind-data pipeline.

Direction must correspond to the supplied wind vector.

Speed must influence particle movement speed and trail appearance.

Do not make wind animation purely decorative.

Clicking the wind layer should expose technical information including
wind speed, meteorological direction, U component, V component, source,
valid time, and data status.

IMPORTANT DISTINCTION:

- The wind visualization may use an external model-derived forecast
  source such as Open-Meteo.
- The existing scientific simulation may still contain deterministic
  synthetic fields for components that are not yet connected to real
  external data.
- Never silently present synthetic fields as observations.
- Never silently present model forecasts as measured observations.
- Label the provenance of the wind layer explicitly.

============================================================
PHASE 10A — WIND PARTICLE LAYER — LIVE IMPLEMENTATION CONTRACT
============================================================

Purpose:

Implement a Windy.com-style animated wind particle layer for the
Antarctic Sea-Ice / Iceberg Navigation Decision Support dashboard
(SIH PS 26059, NCPOR/MoES).

The goal is a scientifically connected, visually convincing wind layer
with no paid service or API key anywhere in the pipeline.

------------------------------------------------------------
10A.1 — HOW THE EFFECT WORKS
------------------------------------------------------------

Do not re-derive or hand-roll the particle-advection renderer.

The implementation must follow this model:

1. Obtain U/V wind components on a latitude/longitude grid.
2. Spawn many particles at positions across the visible wind field.
3. On each animation step, sample U/V at the particle position.
4. Advect the particle using the sampled vector.
5. Fade the existing canvas rather than fully clearing it so trails form.
6. Use wind-speed magnitude to influence trail appearance and/or color.
7. Recycle particles when they die or leave the supported field.

Use `leaflet-velocity` for this renderer because it already implements
the required Leaflet canvas particle-advection behaviour.

Do not write a second custom particle engine unless the existing
plugin is proven incompatible with a project requirement and that
decision is documented.

------------------------------------------------------------
10A.2 — LEAFLET / NEXT.JS REQUIREMENTS
------------------------------------------------------------

The project uses Next.js + Leaflet.

Leaflet requires `window`, therefore the wind-capable map component
must be client-only.

Preferred architecture:

`dynamic(() => import('./WindMap'), { ssr: false })`

Import the relevant Leaflet and velocity-layer CSS in the client-side
map path.

`leaflet-velocity` attaches imperatively to a Leaflet map and is not a
React component.

Use one of these patterns:

- a raw Leaflet `L.Map` ref, or
- `useMap()` when the project already uses react-leaflet.

Attach the velocity layer from a controlled `useEffect`.

Do not recreate the velocity layer on every React render.

Keep the wind layer lifecycle explicit:

CREATE
→
ATTACH
→
UPDATE DATA
→
TOGGLE
→
DETACH/CLEAN UP

Avoid duplicate canvas layers and event-listener leaks.

------------------------------------------------------------
10A.3 — DEPENDENCIES
------------------------------------------------------------

Install:

```bash
npm install leaflet leaflet-velocity
npm install --save-dev @types/leaflet
```

`leaflet-velocity` does not provide complete official TypeScript types
in many setups. Use a minimal local `.d.ts` declaration or a narrowly
scoped `// @ts-ignore` only where required.

Do not add a large ambient `any` declaration that hides unrelated type
errors.

For the optional Antarctic Polar Stereographic implementation, install:

```bash
npm install proj4 proj4leaflet
```

Do not add `proj4` / `proj4leaflet` merely to claim polar support.
Use them only if the actual map architecture can support the required
projection and tile source.

------------------------------------------------------------
10A.4 — ANTARCTIC MAP PROJECTION: CRITICAL
------------------------------------------------------------

Leaflet's default CRS is Web Mercator (EPSG:3857).

That projection becomes increasingly distorted toward the poles, so
Antarctica must not be treated like an ordinary mid-latitude web map.

There are two accepted implementation paths.

OPTION A — FAST / DEMO-SAFE:

- Keep EPSG:3857.
- Constrain `maxBounds` and default zoom so the map does not show the
  entire polar cap as one distorted web-mercator scene.
- Keep the camera focused on the operational Southern Ocean /
  Antarctic coastal region.
- Accept some polar stretching as a documented prototype limitation.

This is preferred when changing the base map CRS would destabilize the
existing map or its tile source.

OPTION B — CORRECT POLAR PROJECTION:

Use Antarctic Polar Stereographic (EPSG:3031) through `proj4` +
`proj4leaflet`.

Before switching:

1. Inspect the existing base-map tile source.
2. Verify that the base layer can actually be displayed in the chosen
   CRS.
3. Verify all geometry transforms used by routes, icebergs, coastlines,
   wind grids, and hit-testing.
4. Verify mouse-coordinate conversion.
5. Verify bounds and zoom behaviour.
6. Verify that existing route and land-protection logic still operates.

Do not switch the entire application to EPSG:3031 blindly while keeping
ordinary EPSG:3857 web tiles. A mismatched map CRS can make the map look
broken even though the scientific coordinates are correct.

Treat EPSG:3031 as the preferred stretch target for realistic polar
mapping, not as permission to destabilize a working demo.

Regardless of option A or B, document the chosen projection and its
limitations.

------------------------------------------------------------
10A.5 — WIND DATA SOURCE
------------------------------------------------------------

Use Open-Meteo as the default no-key external wind source for the live
wind visualization layer.

Open-Meteo exposes forecast wind speed and wind direction, supports
multiple comma-separated latitude/longitude coordinates, requires no
API key for the non-commercial use case, and provides data under CC BY
4.0 with attribution requirements.

Primary API concept:

`https://api.open-meteo.com/v1/forecast`

Request wind variables appropriate to the chosen response mode.

For the simplest current-condition implementation, the request may use:

`current=wind_speed_10m,wind_direction_10m`

For time-aware animation or forecast playback, prefer hourly fields so
the wind layer can be tied to a valid simulation/forecast timestamp.

Use:

`wind_speed_unit=ms`

Do not assume the API's default wind unit.

The project must not require:

- a paid weather API
- a commercial token
- a credit card
- a hidden subscription
- a frontend-exposed secret key

Do not put provider keys in client code.

------------------------------------------------------------
10A.6 — GRID SAMPLING
------------------------------------------------------------

Define a configurable Antarctic/Southern Ocean bounding box based on the
existing map operational area rather than hardcoding arbitrary global
coverage.

Start with a coarse grid around 2° spacing for the prototype.

Build the sample points from:

- latitude list
- longitude list

Batch the coordinate requests.

Do not make one HTTP request per grid point.

Open-Meteo accepts multiple coordinate pairs in one request. Keep the
batch size configurable and use a conservative chunk size such as
50–100 locations per request to avoid unnecessarily large requests.

Represent the grid explicitly:

- west longitude
- east longitude
- north latitude
- south latitude
- longitude spacing
- latitude spacing
- number of columns
- number of rows
- valid timestamp

Do not infer grid geometry from array length at the frontend.

------------------------------------------------------------
10A.7 — SPEED/DIRECTION TO U/V
------------------------------------------------------------

Open-Meteo may provide meteorological wind speed and direction rather
than direct U/V components.

Convert them on the backend.

Use the meteorological convention carefully:

```js
const rad = direction * Math.PI / 180;
const u = -speed * Math.sin(rad);
const v = -speed * Math.cos(rad);
```

The negative signs are important because meteorological wind direction
describes the direction the wind is coming FROM, while U/V describe the
vector component in the direction the air is moving.

Do not perform a second conversion in the frontend.

The frontend consumes already-normalized U/V field data.

Validate the conversion with known cardinal cases:

- 0° = wind from north, therefore motion toward south
- 90° = wind from east, therefore motion toward west
- 180° = wind from south, therefore motion toward north
- 270° = wind from west, therefore motion toward east

Add tests so a future refactor cannot silently reverse the animation.

------------------------------------------------------------
10A.8 — LEAFLET-VELOCITY DATA CONTRACT
------------------------------------------------------------

`leaflet-velocity` expects GRIB2-style metadata plus a flat row-major
data array for the U and V components.

The backend should emit two records:

```json
[
  {
    "header": {
      "parameterCategory": 2,
      "parameterNumber": 2,
      "la1": 0,
      "lo1": 0,
      "la2": 0,
      "lo2": 0,
      "dx": 0,
      "dy": 0,
      "nx": 0,
      "ny": 0,
      "refTime": ""
    },
    "data": []
  },
  {
    "header": {
      "parameterCategory": 2,
      "parameterNumber": 3,
      "la1": 0,
      "lo1": 0,
      "la2": 0,
      "lo2": 0,
      "dx": 0,
      "dy": 0,
      "nx": 0,
      "ny": 0,
      "refTime": ""
    },
    "data": []
  }
]
```

The example values above are placeholders only.

At runtime:

- `parameterNumber: 2` = U component
- `parameterNumber: 3` = V component
- `nx` = points east-west
- `ny` = rows north-south
- `dx` = longitudinal spacing
- `dy` = positive grid spacing magnitude
- `la1` = northernmost latitude
- `lo1` = westernmost longitude
- `la2` = southernmost latitude
- `lo2` = easternmost longitude
- `data` = flat row-major component values

CRITICAL ARRAY ORDER:

The flattened data must match the header geometry.

Prefer the convention expected by the velocity renderer:

row 0 = northernmost latitude
row 1 = next latitude south
...
last row = southernmost latitude

Do not rely on an arbitrary `Array.flat()` over an ascending
south-to-north latitude array.

If the source grid is generated south-to-north, reverse the latitude
row order before flattening.

The implementation must verify the exact data contract against the
installed `leaflet-velocity` package/sample data before finalizing the
adapter. Do not assume an undocumented field name or scan order.

Also verify that the produced field has:

`data.length === nx * ny`

for both U and V.

------------------------------------------------------------
10A.9 — BACKEND WIND ENDPOINT
------------------------------------------------------------

Create a dedicated backend/API boundary for wind data.

Preferred endpoint:

`GET /api/wind`

Optional query parameters may include:

- bounds
- grid spacing
- timestamp / forecast hour
- provider/model selection
- refresh flag

The endpoint must:

1. resolve the requested grid,
2. fetch or retrieve cached external wind data,
3. validate the response,
4. convert speed/direction to U/V,
5. assemble the velocity-layer grid,
6. attach provenance metadata,
7. return the field.

Do not put the Open-Meteo HTTP request directly inside a React component.

Do not duplicate U/V conversion in multiple modules.

Recommended conceptual backend separation:

`WindProvider`
→
`WindNormalizer`
→
`WindGridBuilder`
→
`WindCache`
→
`/api/wind`

Keep the provider replaceable so a future NCPOR/IMD or other scientific
dataset can replace Open-Meteo without changing the renderer.

------------------------------------------------------------
10A.10 — CACHING AND REFRESH
------------------------------------------------------------

Wind models are time-dependent, but there is no reason to refetch the
same field on every page render or animation frame.

Use server-side caching.

Acceptable mechanisms include:

- Next.js fetch revalidation where appropriate,
- a controlled in-memory cache for the prototype,
- an existing project cache if already present.

Never cache unbounded arbitrary query combinations.

Cache key should include the meaningful field parameters, such as:

provider
+
grid bounds
+
grid spacing
+
valid time

Refresh on a sensible cadence aligned with the selected provider data.

The particle animation itself must never trigger network requests.

Manual refresh should be explicit and rate-limited.

------------------------------------------------------------
10A.11 — ATTACHING THE VELOCITY LAYER
------------------------------------------------------------

Preferred configuration baseline:

```js
L.velocityLayer({
  displayValues: true,
  data: windData,
  velocityScale: 0.01,
  particleAge: 90,
  particleMultiplier: 1 / 300
}).addTo(map);
```

These are starting values, not sacred constants.

Tune visually after the pipeline is functioning.

The two most important visual controls to tune first are:

- `velocityScale`
- `particleMultiplier`

Also evaluate:

- particle age
- line width
- opacity
- color scale
- display values
- frame rate

Do not maximize particle count just to make the screenshot look busy.

The layer must remain legible alongside:

- sea ice
- icebergs
- routes
- vessel
- risk zones

------------------------------------------------------------
10A.12 — WIND SPEED COLOR / LEGEND
------------------------------------------------------------

Provide a compact legend for wind speed.

The color scale must be deterministic and documented.

Do not use random colors.

Do not imply that color is risk unless the legend explicitly says so.

Wind-speed visualization and navigation-risk visualization are different
semantic channels and must not share ambiguous color meanings.

------------------------------------------------------------
10A.13 — WIND LAYER TOGGLE
------------------------------------------------------------

Provide a compact on/off control.

Requirements:

- toggle must create at most one active wind layer
- toggling off must remove/hide the layer cleanly
- toggling on must reuse cached data when valid
- toggling must not create duplicate canvases
- hidden wind should not continue consuming unnecessary animation work
  if the plugin/API permits clean suspension

Do not make the wind toggle a giant dashboard card.

------------------------------------------------------------
10A.14 — MANUAL REFRESH
------------------------------------------------------------

Provide a compact manual refresh action for the wind layer.

Refresh sequence:

USER ACTION
→
invalidate stale cache entry where appropriate
→
GET /api/wind
→
validate field
→
replace velocity-layer data
→
update provenance/valid-time UI

Do not rebuild the entire simulation trip merely because the visual wind
layer was refreshed.

------------------------------------------------------------
10A.15 — ERROR HANDLING
------------------------------------------------------------

If the external wind provider fails:

- do not crash the entire map
- do not fabricate a "live" field
- keep the last valid cached field if it is still within its declared
  validity window
- label the layer as stale when applicable
- show a compact non-blocking error state

If no valid field exists:

- hide the velocity layer
- report that wind data are unavailable
- keep the rest of the navigation simulation functional

Never silently replace missing live/model wind data with random vectors.

------------------------------------------------------------
10A.16 — WIND METADATA / TECHNICAL INSPECTOR
------------------------------------------------------------

When the user selects wind or opens the wind inspector, show at least:

- source/provider
- model if known
- variable
- wind speed
- meteorological direction
- U component
- V component
- valid timestamp
- fetch timestamp
- grid resolution
- bounds
- data status
- whether the displayed field is cached/stale

Normal mode should remain compact.

Technical mode should expose the full metadata.

------------------------------------------------------------
10A.17 — WIND DATA AND THE SCIENTIFIC SIMULATION
------------------------------------------------------------

Do not automatically assume that the live wind visualization becomes
the force field used by the iceberg RK45 simulation.

Integration paths must be explicit.

PHASE 1:

Use the Open-Meteo field for the visual wind layer while preserving the
existing deterministic simulation environment and physics.

PHASE 2, ONLY AFTER VALIDATION:

Introduce the provider through `EnvironmentProvider` so the simulation
can consume a normalized wind field.

PHASE 3:

Use the same verified wind field for both:

- visualization
- iceberg/environment calculations

when the spatial, temporal, and coordinate conventions have been
validated.

Until then, clearly label them as separate layers.

This prevents a visually correct wind map from silently changing the
physical trajectory model.

------------------------------------------------------------
10A.18 — PROJECTION / WIND GRID COORDINATE CONSISTENCY
------------------------------------------------------------

The wind API grid is defined in WGS84 latitude/longitude.

The renderer may be operating in:

- EPSG:3857, or
- EPSG:3031

The wind field's underlying geographic coordinates must remain
unambiguous.

If using EPSG:3031:

- transform rendering coordinates through the map CRS,
- do not alter the actual lat/lon values in the data contract,
- ensure particle sampling and map hit-testing remain consistent.

Never "fix" projection distortion by manually altering latitude or
longitude values.

------------------------------------------------------------
10A.19 — PERFORMANCE
------------------------------------------------------------

Separate:

WIND DATA REFRESH RATE

from:

PARTICLE RENDER FRAME RATE

The backend/network layer updates at a controlled cadence.

The canvas renderer animates smoothly between data fetches.

Do not make an HTTP request for every frame.

Do not rebuild the wind grid every frame.

Do not call expensive scientific calculations from particle-render
callbacks.

Use the browser only for rendering and lightweight interpolation.

------------------------------------------------------------
10A.20 — DEFINITION OF DONE FOR WIND
------------------------------------------------------------

The wind layer is complete only when all are true:

[ ] animated particles visibly move
[ ] movement direction matches the supplied wind vector
[ ] speed influences apparent movement
[ ] U and V values come from a real backend data path
[ ] Open-Meteo is reachable through the backend provider
[ ] no paid API key is required
[ ] no client-side secret is required
[ ] response is cached
[ ] the layer does not refetch every render/frame
[ ] the field is converted into the velocity-layer data contract
[ ] `data.length === nx * ny` for U and V
[ ] north-to-south row ordering is correct
[ ] meteorological direction convention is handled correctly
[ ] wind-layer toggle works
[ ] manual refresh works
[ ] provider failure does not crash the map
[ ] stale cached data are labeled
[ ] technical inspector exposes provenance and valid time
[ ] map remains usable over Antarctic latitudes
[ ] no duplicate velocity canvas is created
[ ] browser console has no wind-layer errors
[ ] the limitation of the chosen CRS is documented
[ ] the layer is visually subordinate to vessel / route / hazard layers
  when those layers overlap

============================================================
PHASE 11 — CURRENT ANIMATION
============================================================

Add ocean-current visualization.

Use:

- moving particles
- directional traces
- streamlines

Current direction and speed come from backend.

This visualization should help explain iceberg movement.

============================================================
PHASE 12 — WAVE VISUALIZATION
============================================================

Show subtle moving wave patterns.

Wave intensity should correspond to wave height.

Wave direction should affect visual movement.

Do not allow this layer to overpower the route/iceberg layers.

============================================================
PHASE 13 — ICEBERG ANIMATION
============================================================

Actual iceberg:

moves according to current simulated state.

Predicted path:

separate visual style.

Forecast labels:

+6h
+12h
+24h
+48h
+72h

Iceberg icon should rotate toward movement heading when appropriate.

Movement should be smooth.

Do not teleport the marker every simulation update.

Interpolate between backend states for visual smoothness.

============================================================
PHASE 14 — PHYSICS VISUALIZATION MODE
============================================================

When an iceberg is selected:

show optional physics mode.

Visualize:

wind forcing vector
current forcing vector
Coriolis vector
resultant acceleration
velocity vector
heading

Display actual numerical values.

Example layout:

WIND FORCE        →
CURRENT FORCE     ↗
CORIOLIS          ↓
RESULTANT         →

Use backend values.

Do not fabricate them.

Allow evaluator to understand:

"Why is this iceberg moving this way?"

============================================================
PHASE 15 — ROUTE VISUALIZATION
============================================================

Display:

Reference Route A
Reference Route B
Reference Route C
Actual Vessel Route

Use strong visual differentiation.

The actual route should be visually dominant.

Reference routes should remain visible but secondary.

When rerouting occurs:

OLD ACTUAL ROUTE
        ↓
CHANGE REGION
        ↓
NEW ACTUAL ROUTE

Animate the transition where practical.

============================================================
PHASE 16 — DYNAMIC ROUTE REPLANNING
============================================================

Rerouting should occur because of actual simulated changes.

Possible triggers:

- iceberg conflict
- iceberg approaching route
- rising sea-ice risk
- route cell becomes blocked
- environmental risk increases
- predicted future conflict
- fuel optimization opportunity

The system should not reroute randomly.

Every reroute should have a cause.

============================================================
PHASE 17 — ROUTE DECISION EXPLANATION
============================================================

Every major route decision should be explainable.

Example:

"The original corridor became unsafe because predicted iceberg proximity increased."

Technical version:

"Predicted iceberg corridor intersected the route-risk buffer at +24h. Composite risk increased from 0.39 to 0.72. A* recalculated the route with iceberg penalty weighting enabled."

Another example:

"The vessel moved toward a longer route because it reduced navigation risk."

Technical:

"Distance increased by 84 km while estimated composite risk decreased by 31%."

Use actual backend calculations.

============================================================
PHASE 18 — EVENT STORY ENGINE
============================================================

Events should tell a story, not just display logs.

Event sequence example:

EVENT 1
ICEBERG DETECTED

EVENT 2
ICEBERG APPROACHING REFERENCE CORRIDOR

EVENT 3
RISK INCREASING

EVENT 4
ROUTE CONFLICT

EVENT 5
NAVIGATION RE-EVALUATION

EVENT 6
NEW ROUTE CALCULATED

EVENT 7
VESSEL TURNING

EVENT 8
VESSEL ON NEW ROUTE

EVENT 9
RISK REDUCED

Every event should contain:

timestamp
event_type
severity
title
plain_language_message
technical_explanation
related_object
related_coordinates

============================================================
PHASE 19 — EXPLAIN MODE
============================================================

Add:

NORMAL MODE
TECHNICAL MODE

NORMAL MODE:

Designed for:

- judges
- general viewers
- demonstration audience

Example:

"Sea ice is becoming denser ahead of the ship. The route is becoming less suitable."

TECHNICAL MODE:

"Sea-ice concentration increased from 0.44 to 0.67 over the next 18 hours. Route navigation-risk score increased from 0.32 to 0.58."

The normal view should communicate the idea.

Technical view should communicate the mechanism.

============================================================
PHASE 20 — VOYAGE PLAYBACK
============================================================

The voyage should work like a video.

Provide:

PLAY
PAUSE
RESTART
STEP BACK
STEP FORWARD

Timeline:

- continuous
- draggable
- event markers
- reroute markers
- iceberg detection markers
- risk transition markers

Speed controls:

0.5x
1x
2x
5x
10x
50x

Clicking an event should seek to that time.

============================================================
PHASE 21 — TRIP CREATION
============================================================

Trip creation should allow:

origin
destination
departure scenario
vessel
seed

Optionally:

scenario type
environment severity
departure date

Every trip receives a unique ID and deterministic seed.

Same seed:

same environment
same iceberg scenario
same physics
same route evolution

Different seed:

different scientific scenario.

============================================================
PHASE 22 — MULTIPLE VESSELS
============================================================

Architect the system so vessel properties can eventually vary.

Possible properties:

- cruise speed
- maximum speed
- acceleration
- turn rate
- fuel capacity
- fuel consumption
- ice capability
- safety margin

Do not hardcode these into the route engine.

Use vessel configuration.

This makes the prototype extensible.

============================================================
PHASE 23 — RISK SYSTEM
============================================================

Create clearly separated risks:

SEA_ICE_RISK
ICEBERG_RISK
ENVIRONMENT_RISK
OVERALL_NAVIGATION_RISK

Do not collapse them internally too early.

Allow evaluator to see the contributors.

Composite risk should be explainable.

Example:

Overall Risk:
0.71

Contributors:

Sea ice:
0.52

Iceberg:
0.88

Environment:
0.31

This should actually correspond to the backend model.

============================================================
PHASE 24 — SAFETY MODEL
============================================================

Define clear route classifications:

SAFE
CAUTION
HIGH_RISK
BLOCKED

Safety classification should come from actual thresholds.

Avoid arbitrary frontend-only colouring.

============================================================
PHASE 25 — FUEL MODEL
============================================================

Fuel estimate should respond to:

- vessel speed
- travel distance
- environmental conditions
- route length
- possibly ice conditions

Do not show a completely static fuel number.

Fuel should decrease as the vessel travels.

Route comparisons should report expected fuel.

============================================================
PHASE 26 — ETA MODEL
============================================================

ETA should update dynamically.

ETA depends on:

remaining distance
+
vessel speed
+
route conditions

When rerouting occurs:

ETA can change.

Show:

previous ETA
new ETA
ETA difference

This should become part of route-change events.

============================================================
PHASE 27 — REFERENCE ROUTE ANALYTICS
============================================================

Each reference route should have:

distance
duration
fuel
sea-ice risk
iceberg risk
environment risk
overall risk
safety score

Allow the user to click a reference route.

The user should understand why that route exists.

============================================================
PHASE 28 — ACTUAL ROUTE ANALYTICS
============================================================

The actual route should show:

current distance
remaining distance
expected duration
remaining duration
fuel used
estimated remaining fuel
risk
safety score
current route reason

Example explanation:

"Selected because it provided the lowest weighted navigation cost under current conditions."

============================================================
PHASE 29 — ROUTE CHANGE COMPARISON
============================================================

Whenever route changes:

show a compact comparison.

Before:

Risk: 0.74
Fuel: 82 t
Distance: 5,400 km
ETA: 11.3 days

After:

Risk: 0.41
Fuel: 85 t
Distance: 5,520 km
ETA: 11.6 days

Then explain:

"Safer route selected at the cost of 120 km and 0.3 days."

Use actual values.

============================================================
PHASE 30 — ADVANCED MAP LAYERS
============================================================

Support toggling:

SEA ICE
ICEBERGS
ICEBERG TRAJECTORIES
WIND
CURRENT
WAVES
REFERENCE ROUTES
ACTUAL ROUTE
RISK ZONES
EVENTS
VESSEL

Layer controls should be compact.

Avoid giant menu panels.

============================================================
PHASE 31 — MAP DEPTH AND VISUAL HIERARCHY
============================================================

The map should remain readable even with many layers.

Recommended visual priority:

1. Vessel
2. Actual route
3. Major hazards
4. Reference routes
5. Icebergs
6. Sea ice
7. Wind/current
8. Background geography

The background must never overpower the scientific layers.

============================================================
PHASE 32 — CINEMATIC SIMULATION FEEL
============================================================

Add restrained cinematic elements:

- smooth camera transitions
- subtle layer fades
- route transition animations
- event focus
- object highlighting
- intelligent zoom
- smooth tooltip appearance
- selected-object emphasis

Do not turn the project into a game without scientific meaning.

The visual style should communicate:

"serious scientific simulation"

rather than:

"arcade game".

============================================================
PHASE 33 — EVENT CAMERA
============================================================

When an important event occurs, optionally provide:

- subtle camera movement
- temporary object highlighting
- event indicator
- focus on relevant region

Example:

ICEBERG ROUTE CONFLICT

→ highlight iceberg
→ highlight route segment
→ display risk region
→ show event message
→ route recalculation
→ show new route

Do not forcibly move the camera during every event.

Make this optional or restrained.

============================================================
PHASE 34 — VISUAL STORYTELLING MODE
============================================================

Add an optional mode where the simulation explains itself visually.

Example:

"ICEBERG DETECTED"

↓
iceberg highlighted

"TRAJECTORY APPROACHING ROUTE"

↓
forecast trajectory illuminated

"RISK INCREASING"

↓
risk zone expands/highlights

"ROUTE RECALCULATED"

↓
old route fades
new route appears

"VESSEL TURNING"

↓
ship changes heading

"SAFE CORRIDOR FOUND"

↓
risk indicator drops

This should be one of the strongest demonstration sequences.

============================================================
PHASE 35 — EDUCATIONAL VISUALIZATION
============================================================

A normal person should understand:

Wind pushes the iceberg.

Current influences its movement.

Coriolis affects direction.

Sea ice changes route cost.

Icebergs affect navigation risk.

Risk changes the navigation grid.

The optimizer chooses a new route.

The vessel follows it.

This should be visible.

============================================================
PHASE 36 — TECHNICAL INSPECTION MODE
============================================================

Add an optional technical panel.

Show:

simulation time
seed
environment values
sea-ice values
iceberg physics
route costs
risk contributors
optimization values
vessel state

Include scientific terms only where helpful.

============================================================
PHASE 37 — DETERMINISTIC REPLAY
============================================================

Critical requirement:

Replay must reconstruct the same voyage.

Do not store only the final route.

Store:

seed
scenario parameters
simulation clock
event definitions
deterministic model parameters

When seeking:

reconstruct state deterministically.

Verify:

same timestamp
→ same state

same trip
→ same event sequence

same seed
→ same environment

============================================================
PHASE 38 — TRIP HISTORY
============================================================

Maintain history:

Trip ID
Seed
Origin
Destination
Duration
Distance
Fuel
Reroutes
Major Events
Final Risk
Final Status

Allow replay.

============================================================
PHASE 39 — PERFORMANCE ARCHITECTURE
============================================================

Do not run heavy calculations every animation frame.

Separate:

SIMULATION UPDATE RATE

from:

RENDER FRAME RATE

For example:

simulation:
scientific state updates

rendering:
smooth interpolation

This means:

backend state changes at controlled simulation steps

frontend interpolates between states visually

Do not recalculate RK45 trajectories every browser frame.

Cache expensive computations.

============================================================
PHASE 40 — FRONTEND STATE ARCHITECTURE
============================================================

Frontend should maintain:

CurrentTripState
CurrentSimulationTime
PlaybackState
SelectedObject
VisibleLayers
AnimationState
EventState
UIState

But the backend remains the scientific source of truth.

Frontend state should represent visualization state, not scientific truth.

============================================================
PHASE 41 — API CONSISTENCY
============================================================

Important endpoints include:

POST /api/trips
GET /api/trips
GET /api/trips/{trip_id}
POST /api/trips/{trip_id}/start
POST /api/trips/{trip_id}/pause
POST /api/trips/{trip_id}/reset
POST /api/trips/{trip_id}/step
POST /api/trips/{trip_id}/seek
POST /api/trips/{trip_id}/speed
GET /api/trips/{trip_id}/state
GET /api/trips/{trip_id}/timeline
GET /api/trips/{trip_id}/events

Existing endpoints:

GET /api/sea-ice
GET /api/icebergs
POST /api/icebergs/predict
POST /api/routes/optimize
GET /api/environment
GET /api/wind
GET /api/health

`GET /api/wind` is the dedicated boundary for the live/model-derived
wind visualization field.

The frontend must not call Open-Meteo directly.

Use the actual backend scientific models and provider abstractions.

Do not create duplicate equations inside API modules.

Do not duplicate wind-direction-to-U/V conversion outside the canonical
wind normalization module.

============================================================
PHASE 42 — BACKEND SOURCE OF TRUTH
============================================================

Architecture:

FASTAPI
    ↓
TRIP ENGINE
    ↓
SCIENTIFIC SIMULATION
    ↓
ENVIRONMENT
    ↓
SEA ICE
    ↓
ICEBERGS
    ↓
RISK
    ↓
ROUTE OPTIMIZATION
    ↓
VESSEL MOTION
    ↓
STATE SNAPSHOT
    ↓
FRONTEND

Frontend only visualizes state.

============================================================
PHASE 43 — SCIENTIFIC PERFORMANCE
============================================================

Benchmark:

- one iceberg trajectory
- multiple iceberg trajectories
- sea-ice grid generation
- wind grid generation
- wind provider request + cache hit
- velocity-layer data assembly
- route optimization
- full trip step
- full trip replay

Track execution times.

For wind specifically, verify:

- cached requests do not refetch unnecessarily
- particle rendering does not perform network work
- wind-layer toggling does not create duplicate canvases
- wind-data refresh does not stall simulation playback

Avoid unnecessary recomputation.

============================================================
PHASE 44 — TESTING STRATEGY
============================================================

Add/maintain tests for:

ENVIRONMENT
- deterministic values
- spatial continuity
- temporal continuity

WIND
- provider response validation
- speed/direction conversion to U/V
- cardinal-direction conversion cases
- grid bounds
- grid spacing
- nx/ny consistency
- row ordering
- `data.length === nx * ny`
- cache behaviour
- stale-data handling
- provider failure handling
- no duplicate layer creation

SEA ICE
- valid concentration
- valid thickness
- valid category
- valid risk
- FAST_ICE persistence
- BLOCKED logic

ICEBERGS
- force calculations
- Coriolis
- RK45 integration
- geometry
- land constraints
- grounding

ROUTING
- cost grid
- blocked cells
- A*
- route scoring
- rerouting

VESSEL
- smooth movement
- heading
- acceleration
- turn rate
- fuel
- ETA

TRIPS
- creation
- start
- pause
- step
- seek
- replay
- reset
- determinism

EVENTS
- detection
- approaching
- conflict
- recalculation
- vessel response

============================================================
PHASE 45 — FULL VALIDATION
============================================================

After implementation:

Run:

.\ice\Scripts\python.exe -m pytest

Do not stop after one test file.

Then start:

.\ice\Scripts\python.exe -m uvicorn backend.app:app --reload

Verify:

/api/health

Then perform browser validation.

============================================================
PHASE 46 — BROWSER TEST SCENARIO
============================================================

Perform this exact demonstration:

1. Open application.

2. Create new trip.

3. Select:

Cape Town
→
Bharati access

4. Start simulation.

5. Watch vessel departure.

6. Watch sea-ice surface.

7. Watch environmental movement.

8. Click sea ice.

9. Inspect thickness and risk.

10. Click iceberg.

11. Inspect trajectory.

12. Activate technical physics view.

13. Continue simulation.

14. Let iceberg approach route.

15. Observe risk increase.

16. Observe route conflict.

17. Observe route recalculation.

18. Observe old route and new route.

19. Observe vessel heading change.

20. Observe vessel follow new path.

21. Open event timeline.

22. Click reroute event.

23. Seek backward.

24. Replay.

25. Verify same state appears again.

============================================================
PHASE 47 — VISUAL QA
============================================================

Look for:

- overlapping labels
- marker jitter
- route flicker
- iceberg teleportation
- incorrect headings
- invalid coordinates
- land penetration
- unreadable risk overlays
- excessive visual clutter
- stale telemetry
- timeline desynchronization
- incorrect selected-object information
- frontend errors
- API failures

Fix these before finalizing.

============================================================
PHASE 48 — RESPONSIVE DESIGN
============================================================

Application should work at:

desktop
laptop
smaller screens

Desktop should be the primary target.

Do not sacrifice desktop scientific visualization merely to support mobile.

============================================================
PHASE 49 — ADVANCED UI SYSTEM
============================================================

Build reusable components for:

- telemetry overlays
- object inspectors
- event cards
- route information
- layer controls
- playback controls
- timeline
- technical data panels
- explanation panels

Avoid a giant monolithic index.html.

============================================================
PHASE 50 — VISUAL DESIGN SYSTEM
============================================================

Create a consistent design language.

Use:

- dark scientific background
- restrained accent colours
- translucent overlays
- subtle borders
- soft shadows
- clean typography
- consistent spacing
- compact controls

Risk colours must be consistent.

Example conceptual hierarchy:

low
→ safe visual

moderate
→ caution

high
→ warning

extreme
→ strong warning

blocked
→ prohibited

Do not use random colours for the same concept.

============================================================
PHASE 51 — FINAL PRESENTATION MODE
============================================================

Add a presentation-friendly mode.

When enabled:

reduce clutter

show:

- vessel
- actual route
- reference routes
- major icebergs
- sea ice
- environment
- events

Hide technical details until clicked.

This should be excellent for an SIH demonstration.

============================================================
PHASE 52 — TECHNICAL DEMONSTRATION MODE
============================================================

A technical evaluator should be able to inspect:

- simulation seed
- mathematical parameters
- environmental state
- sea-ice model
- iceberg physics
- route cost
- route weights
- optimization result
- vessel state
- risk contributors

Do not force all of this onto the main map.

============================================================
PHASE 53 — DOCUMENTATION
============================================================

Update/create documentation for:

docs/
    architecture.md
    physics_model.md
    prediction_model.md
    route_optimization.md
    environment_model.md
    simulation_engine.md
    frontend_architecture.md
    event_system.md
    api_contract.md
    wind_layer.md
    data_providers.md

Document:

- architecture
- equations
- assumptions
- constraints
- limitations
- simulation workflow
- routing logic
- risk logic
- deterministic replay
- wind particle rendering architecture
- Open-Meteo provider usage and attribution
- wind grid / U-V normalization
- wind cache and refresh strategy
- Antarctic map projection choice
- EPSG:3857 limitations and/or EPSG:3031 implementation
- data provenance and stale-data handling

============================================================
PHASE 54 — SCIENTIFIC DISCLAIMER
============================================================

Use exactly:

"This prototype uses synthetic scientific simulation fields for development and demonstration. These values are not real-time observations and are not suitable for operational navigation."

Display this in the application and documentation.

Because the wind visualization can use an external model-derived
forecast source, also display a separate provenance note making clear
that model forecast data are not direct measurements.

Never label forecast-model data as observed data.

Never imply operational certification.

============================================================
PHASE 55 — DATA ARCHITECTURE FOR FUTURE REAL DATA
============================================================

Design provider interfaces so synthetic simulation can eventually be replaced by:

- satellite-derived sea-ice datasets
- ocean current datasets
- meteorological datasets
- iceberg observations

without rewriting:

- frontend
- route engine
- vessel simulation
- event system

Use provider abstraction.

Example concept:

EnvironmentProvider
WindProvider
SeaIceProvider
IcebergProvider

For wind specifically, keep this chain replaceable:

WindProvider
→
WindNormalizer
→
WindGridBuilder
→
WindCache
→
API
→
Leaflet Velocity Renderer

The simulation layer should consume a common normalized interface.

Do not couple the simulation engine or frontend directly to Open-Meteo.

A future provider such as an NCPOR/IMD or other authoritative polar
dataset should be able to replace Open-Meteo without rewriting:

- the frontend renderer
- wind-layer controls
- route engine
- vessel simulation
- event system

============================================================
PHASE 56 — FUTURE MACHINE LEARNING INTEGRATION
============================================================

Keep the architecture ready for future learned predictive models.

Potential future models:

- sea-ice forecasting
- iceberg trajectory correction
- risk prediction
- route-duration prediction

But do not make the prototype depend on unavailable datasets.

The current system should function entirely using the deterministic scientific simulation.

Where learned models are used, keep them replaceable.

============================================================
PHASE 57 — FAILURE HANDLING
============================================================

Handle:

- invalid trip
- impossible destination
- missing state
- route unavailable
- fully blocked corridor
- empty iceberg result
- invalid coordinates
- invalid simulation time
- API timeout
- frontend stale state

Never silently display misleading data.

Show understandable messages.

============================================================
PHASE 58 — LOGGING
============================================================

Backend logs should provide meaningful diagnostics.

Examples:

Trip created
Simulation started
Route generated
Iceberg conflict detected
Route recalculation triggered
Route changed
Trip paused
Trip reset

Do not flood console logs every animation frame.

============================================================
PHASE 59 — CODE QUALITY
============================================================

Follow:

- clear naming
- type hints
- modular functions
- reusable components
- comments only where useful
- docstrings for scientific functions
- configuration separated from algorithms
- no duplicate equations
- no unnecessary globals

Keep scientific formulas readable.

============================================================
PHASE 60 — NO FRONTEND SCIENTIFIC DUPLICATION
============================================================

This rule is absolute.

JavaScript must NOT reproduce:

- iceberg equations
- sea-ice equations
- A*
- route scoring mathematics
- risk equations

Backend computes.

Frontend renders.

============================================================
PHASE 61 — ADVANCED VISUAL INTERPOLATION
============================================================

Scientific state updates may be discrete.

Visual movement should be continuous.

For example:

backend:

t = 10
ship = position A

t = 11
ship = position B

frontend:

smoothly interpolate A → B

Same for:

- iceberg
- vessel
- environment particles
- route transitions
- forecast markers

Do not alter scientific state when interpolating visually.

============================================================
PHASE 62 — OBJECT SELECTION SYSTEM
============================================================

Only one major object should normally be selected at a time.

Selection should:

- highlight object
- show context panel
- dim unrelated information
- provide close inspection

Click empty map:

clear selection

Click new object:

replace selection

============================================================
PHASE 63 — CONTEXTUAL INFORMATION DESIGN
============================================================

Do not make information feel like traditional dashboard cards.

Use:

- floating panels
- anchored information
- side inspector
- map labels
- compact overlays

Context should depend on what was clicked.

============================================================
PHASE 64 — EVENT FOCUS
============================================================

Events should link to objects.

Example:

ICEBERG_ROUTE_CONFLICT

Event click:

→ seek to event time
→ highlight iceberg
→ highlight route conflict area
→ open explanation
→ show technical metrics

============================================================
PHASE 65 — SCENARIO VARIATION
============================================================

Different seeds should produce different stories.

Example scenario:

Scenario A:

low ice
few icebergs
stable wind

Scenario B:

high ice
dense iceberg field
strong currents

Scenario C:

dynamic conditions
multiple hazards
multiple reroutes

All remain scientifically constrained.

============================================================
PHASE 66 — REPEATABLE DEMONSTRATION
============================================================

Create one or more demonstration seeds that reliably produce interesting events.

Example:

Demo Seed:
produces iceberg route conflict around a chosen simulation period.

This lets the SIH demonstration reliably show:

detection
→ risk increase
→ rerouting
→ vessel turning
→ successful avoidance

Do not hardcode visual events.

The seed should generate the conditions.

============================================================
PHASE 67 — NO CHEATING
============================================================

Do not:

- move an iceberg randomly toward the vessel just to trigger an event
- fabricate route conflicts
- fabricate risk values
- teleport vessels
- fabricate route metrics
- animate an event without backend state

Interesting behaviour must emerge from simulation conditions.

============================================================
PHASE 68 — SCIENTIFIC HONESTY
============================================================

Always distinguish:

SIMULATION
FORECAST
OBSERVATION

The core prototype currently uses synthetic simulation where
external scientific providers are not connected.

The wind visualization is an explicit exception when `/api/wind` is
connected to the external Open-Meteo provider.

Therefore distinguish:

SIMULATION
- deterministic internal fields used for the simulation engine

FORECAST / MODEL-DERIVED WIND
- external numerical-weather-model wind data used by the live wind layer

OBSERVATION
- measured or satellite-derived observations, only when actually
  connected

Do not label synthetic fields as:

real-time
observed
live satellite
operational

Do not label a numerical forecast as an observation.

Do not label a cached model field as "live" when it is stale.

Every externally sourced wind field must expose provider/provenance and
valid time.

============================================================
PHASE 69 — ARCHITECTURAL EXTENSIBILITY
============================================================

Keep these components replaceable:

EnvironmentProvider
WindProvider
WindNormalizer
WindGridBuilder
SeaIceModel
IcebergModel
RouteOptimizer
VesselModel
RiskModel
EventEngine
Renderer

The system should be modular enough to improve individual components later.

============================================================
PHASE 70 — FINAL USER EXPERIENCE
============================================================

The final user experience should communicate this story naturally:

------------------------------------------------------------

THE VOYAGE STARTS

Cape Town

↓


ENVIRONMENT APPEARS

Wind
Current
Waves
Sea ice

↓


VESSEL DEPARTS

Actual route appears

Three reference routes appear

↓


ICEBERGS APPEAR

Current positions

Forecast trajectories

↓


ENVIRONMENT CHANGES

Sea ice evolves

Wind changes

Current changes

Iceberg trajectories change

↓


HAZARD DEVELOPS

Iceberg approaches corridor

Risk increases

↓


NAVIGATION SYSTEM RESPONDS

Cost field changes

Route recalculated

↓


VESSEL RESPONDS

Heading changes

Vessel turns smoothly

↓


NEW PATH

Actual route moves away from hazard

↓


RISK REDUCES

Voyage continues

↓


REPLAY

User can replay exactly the same event

------------------------------------------------------------

The user should understand this story without reading documentation.

============================================================
PHASE 71 — ADVANCED DEMONSTRATION SEQUENCE
============================================================

Create a polished demonstration sequence.

Scene 1:
Map opens.

Scene 2:
Cape Town highlighted.

Scene 3:
Destination highlighted.

Scene 4:
Reference routes appear.

Scene 5:
Actual route appears.

Scene 6:
Vessel begins moving.

Scene 7:
Wind/current animations become visible.

Scene 8:
Sea ice evolves.

Scene 9:
Icebergs appear.

Scene 10:
One iceberg forecast approaches a reference corridor.

Scene 11:
Risk increases.

Scene 12:
Event appears:

"ICEBERG APPROACHING ROUTE"

Scene 13:
Risk zone becomes visible.

Scene 14:
Optimization triggers.

Scene 15:
Old actual route becomes secondary.

Scene 16:
New actual route appears.

Scene 17:
Vessel begins turning.

Scene 18:
New route is followed.

Scene 19:
Risk decreases.

Scene 20:
Event:

"ROUTE ADJUSTMENT SUCCESSFUL"

Scene 21:
User can pause.

Scene 22:
User can inspect technical metrics.

Scene 23:
User rewinds.

Scene 24:
Simulation reproduces the same sequence.

============================================================
PHASE 72 — ACCESSIBILITY OF INFORMATION
============================================================

Every complex scientific object should have:

short explanation
+
technical details

Example:

SHORT:

"High sea-ice concentration"

TECHNICAL:

Concentration:
0.81

Thickness:
1.74 m

Category:
VERY_CLOSE_ICE

Navigability:
HIGH_RISK

This layered explanation is important.

============================================================
PHASE 73 — FINAL VALIDATION MATRIX
============================================================

Before declaring completion, verify all of the following.

SCIENTIFIC:

[ ] environment deterministic
[ ] sea ice deterministic
[ ] sea ice evolves
[ ] iceberg physics valid
[ ] RK45 preserved
[ ] land constraints valid
[ ] route optimization valid
[ ] risk model valid

SIMULATION:

[ ] simulation clock
[ ] play
[ ] pause
[ ] reset
[ ] seek
[ ] step
[ ] replay
[ ] speed

VESSEL:

[ ] smooth position
[ ] smooth heading
[ ] acceleration
[ ] turn rate
[ ] fuel
[ ] ETA
[ ] dynamic rerouting

ROUTES:

[ ] three reference routes
[ ] actual route
[ ] route separation
[ ] actual route may leave references
[ ] dynamic route optimization
[ ] route comparison

ICEBERGS:

[ ] real simulated movement
[ ] forecast trajectories
[ ] +6h
[ ] +12h
[ ] +24h
[ ] +48h
[ ] +72h
[ ] risk
[ ] grounding
[ ] selection

ENVIRONMENT:

[ ] deterministic simulation environment
[ ] wind particle animation
[ ] wind U/V field from backend
[ ] wind speed/direction are correctly converted
[ ] wind field row ordering is correct
[ ] wind cache works
[ ] wind refresh works
[ ] wind provider failure is handled
[ ] wind provenance is visible
[ ] current animation
[ ] waves
[ ] sea-ice surface
[ ] evolving environment

INTERACTION:

[ ] ship clickable
[ ] iceberg clickable
[ ] sea ice clickable
[ ] route clickable
[ ] wind clickable
[ ] current clickable
[ ] event clickable
[ ] risk zone clickable

STORY:

[ ] events
[ ] explanations
[ ] route conflict
[ ] rerouting story
[ ] vessel response
[ ] timeline synchronization

PERFORMANCE:

[ ] no expensive calculation every browser frame
[ ] trajectory caching
[ ] smooth interpolation
[ ] no UI freeze
[ ] no repeated unnecessary API requests

QUALITY:

[ ] no console errors
[ ] no backend exceptions
[ ] tests pass
[ ] browser validated
[ ] documentation updated

============================================================
PHASE 74 — FINAL TEST COMMANDS
============================================================

Run:

.\ice\Scripts\python.exe -m pytest

Then:

.\ice\Scripts\python.exe -m uvicorn backend.app:app --reload

Verify:

http://127.0.0.1:8000/api/health

Also validate the wind endpoint directly:

http://127.0.0.1:8000/api/wind

Confirm that the response contains valid U/V records and metadata
before testing the browser animation.

Then perform complete browser validation.

============================================================
PHASE 75 — FINAL REPORT
============================================================

When all implementation is complete, provide a final report with exactly these sections:

1. PROJECT STATUS

2. IMPLEMENTED PHASES

3. BACKEND CHANGES

4. SCIENTIFIC MODEL CHANGES

5. ROUTING CHANGES

6. VESSEL SIMULATION CHANGES

7. FRONTEND DESIGN CHANGES

8. ANIMATION SYSTEM

9. INTERACTION SYSTEM

10. EVENT SYSTEM

11. EXPLAIN MODE

12. API CHANGES

13. TEST RESULTS

14. BROWSER VALIDATION

15. PERFORMANCE RESULTS

16. KNOWN LIMITATIONS

17. FUTURE REAL-DATA INTEGRATION PLAN

18. RECOMMENDED NEXT STEP

Include actual files changed.

Do not claim something is implemented unless it was actually implemented and tested.

============================================================
ULTIMATE DESIGN PRINCIPLE
============================================================

The final project must feel like this:

A living Antarctic digital navigation environment.

Not a static dashboard.

Not a slideshow.

Not a fake map.

Not random animation.

The environment evolves.

The physics drives movement.

The predictions anticipate hazards.

The optimization chooses routes.

The vessel responds.

The route changes.

The events tell the story.

The user can inspect everything.

The entire voyage can be replayed.

The result should be scientifically structured, visually impressive, understandable to a normal person, and technically inspectable by an evaluator.

The core loop is:

PREDICT
↓
SIMULATE
↓
OBSERVE
↓
ASSESS RISK
↓
OPTIMIZE
↓
MOVE
↓
REASSESS
↓
RECALCULATE
↓
CONTINUE

Build the entire project around this loop.

============================================================
IMPLEMENTATION DISCIPLINE
============================================================

Do not implement all phases blindly in one uncontrolled rewrite.

Work phase by phase.

At the beginning of each phase:

1. inspect existing implementation
2. identify exact files
3. explain intended modifications
4. implement
5. run focused tests
6. fix failures
7. validate browser behaviour where relevant
8. preserve previous functionality
9. move to the next phase

Never claim completion without validation.

Do not modify unrelated systems.

Do not introduce unnecessary dependencies.

For the wind layer, no paid API, commercial key, subscription, card,
or client-side secret is allowed.

Do not delete working scientific functionality.

Do not replace working architecture without a strong reason.

The goal is not merely to make the project look impressive.

The goal is to make the entire simulation coherent:

SCIENTIFIC MODEL
→
SIMULATION STATE
→
RISK
→
OPTIMIZATION
→
VESSEL BEHAVIOUR
→
VISUALIZATION
→
EXPLANATION

That chain must remain intact throughout the project.