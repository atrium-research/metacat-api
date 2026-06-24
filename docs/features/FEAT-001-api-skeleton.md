# FEAT-001: API skeleton and mock contract

## Summary

The versioned REST API that serves the MetaCat dashboard contract. It returns realistic mocked data through clear endpoints, exposes auto-generated OpenAPI documentation, and is fully containerised.

## Scope

- Pydantic v2 output models as the canonical shared contract.
- Endpoints under `/v1` for catalogues, facets, vocabularies, mappings, snapshots and activity; unversioned `/health` and `/version`.
- Datasource abstraction selected by `DATASOURCE` (`mock` complete, `json` and `sparql` stubs).
- Structured `ErrorResponse` envelope for HTTP and validation errors.

## Business rules

- The smallest queryable unit is a catalogue, on a facet, at a moment in time. The API never returns individual research outputs.
- A facet a catalogue does not expose is reported with an explicit `gap` (or `implicit`) status and a human-readable reason, never a missing field or a silent empty response.
- Every count is a timestamped snapshot, not a live value. Snapshots and timeseries are queryable.
- Facet values carry vocabulary provenance when a controlled vocabulary backs them.
- Cross-catalogue endpoints (`compare`, `overlap`, `timeseries`) are first-class.

## Edge cases

- `compare` returns `null` for a catalogue that does not expose the facet, distinguishing a gap from a zero count.
- Unknown catalogue or vocabulary identifiers return `404` with the `not_found` code.
- Invalid facet or query parameters return `422` with the `validation_error` code.
- `/snapshots/latest` is resolved by the most recent `taken_at`, not by insertion order.

## Data model

Backed by the bundled mock dataset: four catalogues, a six-by-four facet exposure matrix with reasons for every gap and implicit cell, 24 monthly snapshots (May 2024 to May 2026), per-facet monthly timeseries, a vocabulary inventory with concepts, and declared cross-vocabulary mappings.
