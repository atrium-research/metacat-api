"""Harvest ARIADNE facet counts over SPARQL into the metacat-data JSON store.

Carries the SPARQL queries from the ARIADNE_queries_for_metacat notebook in the
metacat-code sibling checkout. The public d4science GraphDB endpoint sits behind
authentication (it answers 302 to anonymous requests), so this script is ready
to run but needs a reachable endpoint: the notebook's d4science instance with
credentials, or the future EOSC EU Node GraphDB. Point it at one with
ARIADNE_SPARQL_ENDPOINT. On an unreachable endpoint it exits without writing,
never fabricating data.

    ARIADNE_SPARQL_ENDPOINT=<url> uv run src/metacat_api/harvesters/harvest_ariadne.py
"""

import os
import sys

from harvest_common import Facets, apply_catalogue, load_store, report, write_store
from SPARQLWrapper import JSON, SPARQLWrapper

ENDPOINT = os.environ.get(
    "ARIADNE_SPARQL_ENDPOINT",
    "https://ariadne-graphdb.cloud.d4science.org/repositories/ariadneplus-pr01",
)

PREFIXES = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX aocat: <https://www.ariadne-infrastructure.eu/resource/ao/cat/1.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

QUERIES = {
    "resource-type": (
        "SELECT ?value (count(?resource) AS ?cnt) WHERE {"
        " ?resource aocat:has_ARIADNE_subject ?as . ?as skos:prefLabel ?value } GROUP BY ?value"
    ),
    "format": (
        "SELECT ?value (count(?resource) AS ?cnt) WHERE {"
        " ?resource aocat:has_data_type ?dt . ?dt skos:prefLabel ?value } GROUP BY ?value"
    ),
    "source": (
        "SELECT ?value (count(?resource) AS ?cnt) WHERE {"
        " GRAPH <https://ariadne-infrastructure.eu/datasourceApis> {"
        " ?g <http://www.d-net.research-infrastructures.eu/provenance/isApiOf> ?value } ."
        " GRAPH ?g { {?resource rdf:type aocat:AO_Collection}"
        " UNION {?resource rdf:type aocat:AO_Individual_Data_Resource} } } GROUP BY ?value"
    ),
    "source-2": (
        "SELECT ?value (count(?resource) AS ?cnt) WHERE {"
        " ?resource aocat:has_publisher ?pub . ?pub aocat:has_name ?value } GROUP BY ?value"
    ),
    "subjects": (
        "SELECT ?value (count(?resource) AS ?cnt) WHERE {"
        " ?resource aocat:has_derived_subject ?s . ?s skos:prefLabel ?value }"
        " GROUP BY ?value ORDER BY DESC(?cnt)"
    ),
}

REASONS = {
    "discipline": "The whole catalogue is archaeology, so discipline is not a queryable facet.",
}


def run_query(client: SPARQLWrapper, query: str) -> list[tuple[str, int]]:
    client.setQuery(PREFIXES + query)
    client.setReturnFormat(JSON)
    rows = client.query().convert()["results"]["bindings"]
    return [(row["value"]["value"], int(row["cnt"]["value"])) for row in rows]


def harvest() -> Facets:
    client = SPARQLWrapper(ENDPOINT)
    try:
        facets: Facets = {facet: run_query(client, query) for facet, query in QUERIES.items()}
    except Exception as error:  # noqa: BLE001
        print(f"ARIADNE endpoint {ENDPOINT} is not queryable: {error}", file=sys.stderr)
        print(
            "Set ARIADNE_SPARQL_ENDPOINT to an authenticated d4science or EOSC GraphDB.",
            file=sys.stderr,
        )
        raise SystemExit(2) from error

    total = sum(count for _, count in facets["resource-type"])
    facets["discipline"] = [("Archaeology", total)]
    return facets


def main() -> None:
    harvested = harvest()
    store = load_store()
    apply_catalogue(
        store, "ariadne", harvested, REASONS, status_overrides={"discipline": "implicit"}
    )
    write_store(store)
    report("ariadne", harvested)


if __name__ == "__main__":
    main()
