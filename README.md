# metacat-api

REST serving layer that catalogues the SSH catalogues: facets and vocabularies over time.

## About MetaCat

MetaCat is the toolset built under ATRIUM (EU Horizon Europe, Grant Agreement No. 101132163), WP3, Task 3.2 (Metadata harmonisation and enrichment). Its goal is to catalogue the catalogues: it systematically describes four major Social Sciences and Humanities European catalogues (ARIADNE Portal, CLARIN VLO, GoTriple, SSH Open Marketplace), their facets, and controlled vocabularies. The audience is data stewards, catalogue maintainers, repository providers and policy makers.

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
set -a && source .env && set +a
uv sync
uv run fastapi dev src/metacat_api/main.py
```

Then open the interactive documentation at http://localhost:8000/docs (or http://localhost:8000/redoc).

## Docker quickstart

```bash
docker compose --env-file .env up --build --force-recreate --watch
```

Then open http://localhost:8000/docs.

### Harvesting real data

The `json` store reads whatever is in `JSON_DATA_DIR`. The harvest scripts in `src/metacat_api/harvesters/` populate it with live data by reusing the connectors from the [`metacat-code`](https://github.com/atrium-research/metacat-code) sibling checkout. They compose: each one updates its own catalogue and keeps the others, so running several in a row keeps every harvested catalogue real.

```bash
uv run src/metacat_api/harvesters/clarin.py
uv run src/metacat_api/harvesters/gotriple.py
uv run src/metacat_api/harvesters/sshomp.py
uv run fastapi dev src/metacat_api/main.py
```

| Connector | Source | Status |
|---|---|---|
| `clarin.py` | CLARIN VLO REST API | Live, public |
| `gotriple.py` | GoTriple aggregation API | Live, public |
| `ariadne.py` | ARIADNE GraphDB (SPARQL) | Ready, needs a reachable endpoint |
| `sshomp.py` | SSHOC/sshompitor weekly item snapshot | Live, public |

The ARIADNE GraphDB is behind authentication (it answers 302 to anonymous requests). The script carries the real SPARQL queries and runs once pointed at an authenticated d4science instance or the future EOSC EU Node GraphDB through `ARIADNE_SPARQL_ENDPOINT`; on an unreachable endpoint it exits without writing. The generated `data/` directory is not committed.

`sshomp.py` : rather than the live SSH Open Marketplace API (whose `item-search` endpoint only aggregates 4 unrelated facets and has no discipline/format aggregation at all), it derives all five non-gap facets from the weekly full-catalogue item dump published by the community [`SSHOC/sshompitor`](https://github.com/SSHOC/sshompitor) monitoring tool, so every facet reflects the same point in time. Set `SSHOMP_SNAPSHOT_DATE=YYYY-MM-DD` to harvest from the nearest snapshot at or before that date instead of the newest one (useful to inspect a past state of the catalogue; each run still fully replaces sshomp's facet data, it does not build up a timeseries).

## Endpoints overview

| Group | Prefix | Purpose |
|---|---|---|
| Catalogues | `/v1/catalogues` | Catalogue list, detail, facet exposure, vocabularies, coverage |
| Facets | `/v1/facets` | Facet list, values, cross-catalogue compare, timeseries |
| Vocabularies | `/v1/vocabularies` | Inventory, detail |
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
