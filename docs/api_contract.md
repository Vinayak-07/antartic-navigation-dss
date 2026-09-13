# API contract

## Health

GET /api/health

Response:
{
  "status": "ok",
  "service": "antarctic-navigation-dss",
  "version": "0.1.0"
}

## Voyage analysis

POST /api/voyage/analyze

Request:
{
  "vessel": "RV Aurora",
  "origin": "Cape Town",
  "destination": "Bharati Station",
  "departure_time": "2026-01-15T06:00:00Z",
  "forecast_horizon_days": 10
}

Response:
{
  "voyage": {},
  "sea_ice": {},
  "icebergs": {},
  "environment": {},
  "routes": {}
}

## Sea-ice forecast

GET /api/sea-ice

Returns sea-ice concentration fields and forecast metadata.

## Iceberg observations

GET /api/icebergs

Returns iceberg positions and risk summary.

## Iceberg prediction

POST /api/icebergs/predict

Returns future positions and uncertainty metrics.

## Route optimization

POST /api/routes/optimize

Returns recommended, shortest, and low-risk alternatives.

## Environmental state

GET /api/environment

Returns weather, ocean, and sea-ice environmental state.

## Contract notes

- TODO: Add strict schema validation when feature development begins.
- PLACEHOLDER: Current responses are mock data aligned to future real schema requirements.
