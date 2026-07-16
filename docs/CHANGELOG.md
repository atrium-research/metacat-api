# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- FastAPI application skeleton serving the MetaCat dashboard contract, with OpenAPI docs at `/docs` and `/redoc`.
- Pydantic v2 output models: catalogues, facet exposures and values, comparisons and timeseries, vocabularies, concepts, mappings, overlaps, snapshots, pagination and error envelope.
- Versioned REST endpoints under `/v1` for catalogues, facets, vocabularies, mappings, snapshots and activity, plus unversioned `/health` and `/version`.
- Datasource abstraction with a complete `mock` backend and typed `json` and `sparql` stubs, selected through the `DATASOURCE` environment variable.
- Realistic mock dataset: four catalogues, the facet exposure matrix with explicit gaps and reasons, 24 monthly snapshots and per-facet timeseries.
- Structured error handling mapping HTTP and validation errors to a stable `ErrorResponse` envelope.
- Docker and docker compose setup, GitHub Actions CI running ruff and pytest.
- Project documentation: README, this changelog, and ADR-001.
- Working `json` datasource reading a `metacat-data` style directory, selected with `DATASOURCE=json`.
- Composable harvest scripts reusing the metacat-code connectors: `harvest_clarin.py` (CLARIN VLO, live), `harvest_gotriple.py` (GoTriple, live) and `harvest_ariadne.py` (ARIADNE SPARQL, ready, needs a reachable endpoint), sharing `harvest_common.py`.
- README corrections describing the real nature of `metacat-code` (query scripts) and `metacat-data` (a curated file repository, not a timestamped snapshot store).
