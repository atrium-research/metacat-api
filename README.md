# metacat-api

REST serving layer that catalogues the SSH catalogues: facets, vocabularies and their mappings, over time.

## About MetaCat

MetaCat is the toolset built under ATRIUM (EU Horizon Europe, Grant Agreement No. 101132163), WP3, Task 3.2 (Metadata harmonisation and enrichment). Its goal is to catalogue the catalogues: it systematically describes four major Social Sciences and Humanities European catalogues (ARIADNE Portal, CLARIN VLO, GoTriple, SSH Open Marketplace), their facets, controlled vocabularies, and the mappings between them. The audience is data stewards, catalogue maintainers, repository providers and policy makers.

## About this repository

`metacat-api` is the serving layer between the MetaCat data sources (a curated reference dataset in `metacat-data` and a GraphDB triplestore modelled with the AO-Cat ontology) and the MetaCat React dashboard (`metacat-dashboard`). It exposes a versioned REST contract with auto-generated OpenAPI documentation. Five principles shape the design:

1. Describe catalogues, not resources. The smallest queryable unit is a catalogue, on a facet, at a moment in time.
2. Gaps are information. When a catalogue does not expose a facet, the API says so explicitly, with a reason.
3. Time is first-class. Counts are timestamped snapshots, and snapshots are queryable.
4. Vocabularies are first-class objects, carrying provenance.
5. Cross-catalogue endpoints (compare, overlap, timeseries) are first-class.

## Quickstart

```bash
git clone https://github.com/atrium-research/metacat-api.git
cd metacat-api

# with uv
uv sync
uv run uvicorn metacat_api.main:app --reload
```

Then open the interactive documentation at http://localhost:8000/docs (or http://localhost:8000/redoc).

## Docker quickstart

```bash
docker compose up --build --force-recreate --watch
```

Then open http://localhost:8000/docs.

## Datasources

The backend is selected with the `DATASOURCE` environment variable:

| Value | Status | Description |
|---|---|---|
| `mock` | complete, default | Serves realistic bundled data. No external dependency. |
| `json` | reads a JSON store | Reads timestamped JSON snapshots from a `metacat-data` style directory (`JSON_DATA_DIR`). |
| `sparql` | roadmap | Queries the GraphDB triplestore on the EOSC EU Node. |

The intended progression is mock, then json, then sparql. See `.env.example` for all settings.

### Harvesting real data

The `json` datasource reads whatever is in `JSON_DATA_DIR` (default `./data`). The harvest scripts in `scripts/` populate it with live data by reusing the connectors from the [`metacat-code`](https://github.com/atrium-research/metacat-code) sibling checkout. They compose: each one updates its own catalogue and keeps the others, so running several in a row keeps every harvested catalogue real. Catalogues that are not harvested fall back to the bundled mock, so the API stays fully populated.

```bash
uv run --with requests --with jq python scripts/harvest_clarin.py
uv run --with requests python scripts/harvest_gotriple.py
DATASOURCE=json JSON_DATA_DIR=./data uv run uvicorn metacat_api.main:app --reload
```

| Connector | Source | Status |
|---|---|---|
| `harvest_clarin.py` | CLARIN VLO REST API | Live, public |
| `harvest_gotriple.py` | GoTriple aggregation API | Live, public |
| `harvest_ariadne.py` | ARIADNE GraphDB (SPARQL) | Ready, needs a reachable endpoint |

The ARIADNE GraphDB is behind authentication (it answers 302 to anonymous requests). The script carries the real SPARQL queries and runs once pointed at an authenticated d4science instance or the future EOSC EU Node GraphDB through `ARIADNE_SPARQL_ENDPOINT`; on an unreachable endpoint it exits without writing. The generated `data/` directory is not committed.

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

- `metacat-code`: per-catalogue query scripts that pull facet counts from each catalogue's API or SPARQL endpoint (a CLARIN query module, ARIADNE and GoTriple notebooks). The harvest scripts in this repo reuse them. (https://github.com/atrium-research/metacat-code)
- `metacat-data`: the datastore. A Baserow reference export (catalogues, sources, providers, resource types, formats) in JSON/XML/RDF, plus per-catalogue facet data such as the CLARIN facets. (https://github.com/atrium-research/metacat-data)
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
