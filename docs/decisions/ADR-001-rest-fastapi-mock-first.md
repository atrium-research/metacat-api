# ADR-001: REST with FastAPI and a mock-first datasource strategy

- Status: Accepted
- Date: 2026-07-15

## Context

`metacat-api` is the serving layer between the MetaCat datastore (timestamped JSON in `metacat-data` and a GraphDB triplestore modelled with AO-Cat) and the MetaCat React dashboard owned by PCSS. The dashboard team needs a stable, self-documenting contract to build against, before the datastore and the GraphDB instance on the EOSC EU Node are wired in. The datastore shape is still moving, so coupling the API to it now would block the frontend and force rework.

## Decision

We expose a versioned REST API built with FastAPI and Pydantic v2. FastAPI gives auto-generated OpenAPI and Swagger for free, and Pydantic v2 models are the canonical shared output contract.

Datasource access goes through an abstract `Datasource` contract with three interchangeable backends selected by the `DATASOURCE` environment variable:

- `mock`: complete and self-sufficient, the default in development.
- `json`: reads the `metacat-data` JSON store.
- `sparql`: queries the GraphDB triplestore.

We build `mock` first and completely. `json` and `sparql` start as typed stubs. The frontend builds against `mock`; backends are swapped in later without touching routes or models.

We do not add an ORM. The datasources are JSON files and a SPARQL endpoint, reached through dedicated adapter modules; plain Python plus Pydantic is enough.

## Consequences

- The frontend can start immediately against a stable contract and realistic data.
- Routes and models are decoupled from storage, so adding `json` and `sparql` is additive.
- The mock dataset must stay realistic enough to exercise every endpoint, including explicit gaps.
- REST (not GraphQL) keeps the contract simple and the OpenAPI documentation authoritative.
