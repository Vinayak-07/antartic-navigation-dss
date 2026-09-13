# Route optimization overview

## Objective

Generate a route that balances travel efficiency with safety risk instead of simply minimizing geographical distance.

## Implemented cost model

Total cost = distance cost + travel time cost + fuel cost + sea-ice risk + iceberg risk + weather risk

## Constraints

- Exclude dangerous areas as hard constraints.
- Respect vessel limitations where applicable.
- Use risk-aware scoring in the route selection process.

## Implemented algorithms

- A*
- Dijkstra
- cost-grid search
- graph-based path optimization

## Current status

- Dynamic latitude/longitude cost grids use sea-ice, iceberg, and weather risk.
- A* searches the grid and excludes blocked unsafe cells.
- Reference, recommended, and conservative round-trip routes are scored with distance, duration, fuel, and risk terms.
- Route safety is reevaluated during playback and rerouting events retain trigger, prior route, new route, risk, and added fuel/distance.

This is a synthetic scientific simulation prototype. It does not represent real Antarctic observations.
