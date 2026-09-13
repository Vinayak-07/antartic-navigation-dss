# Antarctic Sea-Ice, Iceberg Trajectory and Navigation Decision Support System

## Project overview

This project provides the initial scaffold for a voyage decision support system focused on:

1. Sea-ice prediction
2. Iceberg trajectory prediction
3. Navigation route optimization

The repository is intentionally structured for parallel development and mock-first integration. It does not implement production models, live data services, or operational navigation logic yet.

## Current status

- TODO: Replace mock data with real scientific datasets.
- TODO: Implement physical trajectory solver.
- TODO: Implement sea-ice prediction pipeline.
- TODO: Implement route optimization logic.
- PLACEHOLDER: Frontend integration is mocked through API contracts.
- PLANNED: Real environmental data ingestion from NOAA/NSIDC, Copernicus Marine, and ECMWF sources.

## High-level architecture

Data -> Preprocessing -> Environmental features -> sea-ice prediction -> iceberg physics -> risk grid -> route optimization -> decision support -> dashboard

## Operational scenario

- Origin: Cape Town, South Africa
- Destinations: Bharati Station and Maitri Station
- Vessel, departure time, and forecast horizon are selected in the dashboard.
- The system is a navigation decision support tool for human operators, not an autonomous navigation system.

## Strict project rule

This project must not use external generative or prompt-based services. The design is based on physics-based modelling, numerical methods, geospatial computation, scientific datasets, graph algorithms, optimization, and statistical methods.

## Folder layout

See the project tree for the initial structure.

## Mock-first workflow

Frontend interactions are designed to communicate with API endpoints that return mock JSON following the eventual real schemas.

## API endpoints

- GET /api/health
- POST /api/voyage/analyze
- GET /api/sea-ice
- GET /api/icebergs
- POST /api/icebergs/predict
- POST /api/routes/optimize
- GET /api/environment

## Requirements

Please see requirements.txt for the initial dependency list. This is intentionally minimal and suitable for early project setup.

## Notes

This repository is intentionally a scaffold. It is ready for parallel development but includes placeholders throughout the codebase.
