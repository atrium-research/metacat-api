# metacat-api

REST serving layer that catalogues the SSH catalogues: facets, vocabularies and their mappings, over time.

## About MetaCat

MetaCat is the toolset built under ATRIUM (EU Horizon Europe, Grant Agreement No. 101132163), WP3, Task 3.2 (Metadata harmonisation and enrichment). Its goal is to catalogue the catalogues: it systematically describes four major Social Sciences and Humanities European catalogues (ARIADNE Portal, CLARIN VLO, GoTriple, SSH Open Marketplace), their facets, controlled vocabularies, and the mappings between them. The audience is data stewards, catalogue maintainers, repository providers and policy makers.

## About this repository

`metacat-api` is the serving layer between the MetaCat datastore (timestamped JSON in `metacat-data` and a GraphDB triplestore modelled with the AO-Cat ontology) and the MetaCat React dashboard (`metacat-dashboard`). It exposes a versioned REST contract with auto-generated OpenAPI documentation. Five principles shape the design:

1. Describe catalogues, not resources. The smallest queryable unit is a catalogue, on a facet, at a moment in time.
2. Gaps are information. When a catalogue does not expose a facet, the API says so explicitly, with a reason.
3. Time is first-class. Counts are timestamped snapshots, and snapshots are queryable.
4. Vocabularies are first-class objects, carrying provenance.
5. Cross-catalogue endpoints (compare, overlap, timeseries) are first-class.

## Quickstart

Requires Python 3.11+.

```bash
git clone https://github.com/atrium-research/metacat-api.git
cd metacat-api

# with uv (recommended)
uv sync --extra dev
uv run uvicorn metacat_api.main:app --reload

# or with pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn metacat_api.main:app --reload
```

Then open the interactive documentation at http://localhost:8000/docs (or http://localhost:8000/redoc).

## Docker quickstart

```bash
docker compose up
```

Then open http://localhost:8000/docs.

## Datasources

The backend is selected with the `DATASOURCE` environment variable:

| Value | Status | Description |
|---|---|---|
| `mock` | complete, default | Serves realistic bundled data. No external dependency. |
| `json` | roadmap | Reads timestamped JSON snapshots from the `metacat-data` store. |
| `sparql` | roadmap | Queries the GraphDB triplestore on the EOSC EU Node. |

The intended progression is mock, then json, then sparql. See `.env.example` for all settings.

## Endpoints overview

| Group | Prefix | Purpose |
|---|---|---|
| Catalogues | `/v1/catalogues` | Catalogue list, detail, facet exposure, vocabularies, coverage, provenance |
| Facets | `/v1/facets` | Facet list, values, cross-catalogue compare, timeseries |
| Vocabularies | `/v1/vocabularies` | Inventory, detail, paginated concepts |
| Mappings | `/v1/mappings` | Declared mappings and vocabulary overlap |
| Snapshots | `/v1/snapshots` | Snapshot list and latest snapshot metadata |
| Activity | `/v1/activity` | Latest harvest activity per catalogue |
| System | `/health`, `/version` | Liveness probe and version, unversioned |

## Architecture context

- `metacat-code`: harvesting connectors that feed the datastore (https://github.com/atrium-research/metacat-code)
- `metacat-data`: timestamped JSON datastore (https://github.com/atrium-research/metacat-data)
- `metacat-dashboard`: the React dashboard consuming this API (https://github.com/atrium-research/metacat-dashboard)
- ATRIUM: https://github.com/atrium-research

## Contributing

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

## Funding

This work has received funding from the European Union under Grant Agreement No. 101132163 (ATRIUM).
