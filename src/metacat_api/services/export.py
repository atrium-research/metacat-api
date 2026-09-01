import logging
import os
import urllib
from datetime import datetime
from uuid import UUID

import anyio
import rdflib
from anyio import fail_after, open_file, to_thread
from cachetools import LRUCache
from cachetools_async import cached
from rdflib import RDF, RDFS, SKOS, BNode, Graph, Literal, Node, URIRef

from metacat_api.config import settings
from metacat_api.logging_setup import setup_logging
from metacat_api.models import Catalogue, CatalogueVersion, FacetExposure, FacetId, FacetValue, Vocabulary
from metacat_api.models.export import (
    AO_CAT,
    ATRIUM,
    ATRIUM_CATALOGUE,
    ATRIUM_CATALOGUE_VERSION,
    ATRIUM_FACET,
    ATRIUM_FACET_EXPOSURE,
    ATRIUM_FACET_VALUE,
    ATRIUM_VOCABULARY,
    CRM,
    NAMESPACES,
)
from metacat_api.services.catalogues import list_catalogues, list_catalogues_versions
from metacat_api.services.facets import facet_values, list_facets
from metacat_api.services.util import sizeof_fmt
from metacat_api.services.vocabularies import list_vocabularies

logger = logging.getLogger(__name__)


class ExportError(RuntimeError):
    pass


def _encode(term: str) -> str:
    if not term:
        return term
    return urllib.parse.quote_plus(term)


def _to_dimension(
    g: Graph, subject: URIRef, schema: URIRef, value: int | float
) -> list[tuple[Node, Node, Node, Graph]]:
    if not value:
        return []

    triplets = []
    dimension = BNode()
    triplets.append((dimension, RDF.type, AO_CAT.AO_Dimension, g))
    triplets.append((dimension, AO_CAT.has_value, Literal(value), g))
    triplets.append((subject, schema, dimension, g))
    return triplets


def _add_dimension(g: Graph, subject: URIRef, schema: URIRef, value: int | float):
    g.addN(_to_dimension(g, subject, schema, value))


def _add_catalogue(g: Graph, c: Catalogue) -> None:
    subject = ATRIUM_CATALOGUE.term(_encode(c.id))
    g.add((subject, RDF.type, ATRIUM.term("Catalogue")))
    g.add((subject, RDF.type, AO_CAT.AO_Entity))
    g.add((subject, AO_CAT.has_identifier, Literal(c.id)))
    g.add((subject, AO_CAT.has_title, Literal(c.name)))
    g.add((subject, RDFS.label, Literal(c.name)))
    g.add((subject, AO_CAT.has_type, Literal(c.domain)))
    g.add((subject, AO_CAT.has_landing_page, Literal(c.url)))
    g.add((subject, AO_CAT.has_access_rights, Literal(c.licence)))
    g.add((subject, AO_CAT.has_language, Literal(c.languages_summary)))


def _add_vocabulary(g: Graph, v: Vocabulary) -> None:
    subject = ATRIUM_VOCABULARY.term(_encode(v.id))
    g.add((subject, RDF.type, ATRIUM.term("Vocabulary")))
    g.add((subject, RDF.type, AO_CAT.AO_Entity))
    g.add((subject, SKOS.prefLabel, Literal(v.name)))
    g.add((subject, AO_CAT.has_publisher, Literal(v.authority)))
    g.add((subject, AO_CAT.has_landing_page, Literal(v.uri)))


def _add_facet(g: Graph, facet: FacetId) -> None:
    subject = ATRIUM_FACET.term(_encode(facet.value))
    g.add((subject, RDF.type, ATRIUM.term("Facet")))
    g.add((subject, AO_CAT.has_identifier, Literal(facet.name)))
    g.add((subject, AO_CAT.has_identifier, Literal(facet.value)))
    g.add((subject, AO_CAT.has_title, Literal(facet.value)))
    g.add((subject, RDFS.label, Literal(facet.value)))


def _add_facet_exposure(g: Graph, catalogue_id: str, version_id: UUID, fe: FacetExposure) -> None:
    fe_id = f"{catalogue_id}_{version_id}_{fe.facet}"
    subject = ATRIUM_FACET_EXPOSURE.term(_encode(fe_id))
    g.add((subject, RDF.type, ATRIUM.term("FacetExposure")))
    g.add((subject, RDF.type, AO_CAT.AO_Collection))

    g.add((subject, CRM.P2_has_type, ATRIUM_FACET.term(_encode(fe.facet))))

    if fe.status:
        g.add((subject, ATRIUM.has_status, Literal(fe.status)))
    if fe.reason:
        g.add((subject, ATRIUM.has_reason, Literal(fe.reason)))

    if fe.values_count:
        _add_dimension(g, subject, AO_CAT.has_extent, fe.values_count)
    if fe.total_count:
        _add_dimension(g, subject, ATRIUM.has_value_count, fe.total_count)


def _add_catalogue_version(g: Graph, cv: CatalogueVersion):
    cv_id = f"{cv.catalogue_id}_{cv.version_id}"
    subject = ATRIUM_CATALOGUE_VERSION.term(_encode(cv_id))
    g.add((subject, RDF.type, ATRIUM.term("CatalogueVersion")))
    g.add((subject, RDF.type, AO_CAT.AO_Entity))

    g.add((subject, AO_CAT.has_identifier, Literal(cv_id)))
    g.add((subject, AO_CAT.has_identifier, Literal(cv.version_id)))
    g.add((subject, ATRIUM.catalogue, ATRIUM_CATALOGUE.term(_encode(cv.catalogue_id))))

    g.add((subject, CRM.term("P4_has_time-span"), Literal(cv.harvest_at)))

    for voc in cv.vocabularies:
        g.add((subject, ATRIUM.vocabulary, ATRIUM_VOCABULARY.term(_encode(voc))))

    for fe in cv.facet_exposures:
        _add_facet_exposure(g, cv.catalogue_id, cv.version_id, fe)

    _add_dimension(g, subject, AO_CAT.has_extent, cv.total_resources)


def _to_facet_value(g: Graph, fv: FacetValue) -> list[tuple[Node, Node, Node, Graph]]:
    triplets = []
    fv_id = f"{fv.catalogue_id}_{fv.version_id}_{fv.facet}_{fv.value}"
    subject = ATRIUM_FACET_VALUE.term(_encode(fv_id))
    triplets.append((subject, RDF.type, ATRIUM.term("FacetValue"), g))
    triplets.append((subject, RDF.type, AO_CAT.AO_Entity, g))

    triplets.append((subject, ATRIUM.catalogue, ATRIUM_CATALOGUE.term(_encode(fv.catalogue_id)), g))
    cv_uri = ATRIUM_CATALOGUE_VERSION.term(_encode(f"{fv.catalogue_id}_{fv.version_id}"))
    triplets.append((subject, ATRIUM.catalogue_version, cv_uri, g))

    triplets.append((subject, CRM.P2_has_type, ATRIUM_FACET.term(_encode(fv.facet)), g))
    triplets.append((subject, AO_CAT.has_native_subject, Literal(fv.value), g))

    triplets.extend(_to_dimension(g, subject, AO_CAT.has_extent, fv.count))
    return triplets


rdflib.plugin.register(
    "custom_ttl",
    rdflib.plugin.Serializer,
    "metacat_api.models.export",
    "CustomTurtleSerializer",
)


def _compute_ao_cat() -> str:
    logger.info("Start AO-Cat compute")
    start_compute = datetime.now()

    g = Graph()
    for prefix, ns in NAMESPACES.items():
        g.bind(prefix, ns)

    for facet in list_facets():
        _add_facet(g, facet)

    for cat in list_catalogues():
        _add_catalogue(g, cat)

    for cv in list_catalogues_versions():
        _add_catalogue_version(g, cv)

    for voc in list_vocabularies():
        _add_vocabulary(g, voc)

    logger.info("Start get facet values")
    start = datetime.now()
    fvs = facet_values()
    logger.info(f"End get facet values in {datetime.now() - start}")

    logger.info("Start compute facet values")
    start = datetime.now()
    facet_values_triplets = [triplet for fv in fvs for triplet in _to_facet_value(g, fv)]
    logger.info(f"End compute facet values in {datetime.now() - start}")

    logger.info("Start add to graph")
    start = datetime.now()
    g.addN(facet_values_triplets)
    logger.info(f"End add to graph in {datetime.now() - start}")

    logger.info("Start serialize")
    start = datetime.now()
    ttl = g.serialize(format="custom_ttl").strip()
    logger.info(f"End serialize in {datetime.now() - start}")

    logger.info(f"End compute AO-Cat in {datetime.now() - start_compute}")
    return ttl


@cached(cache=LRUCache(maxsize=128))
async def get_ao_cat() -> str:
    with fail_after(300):
        return await to_thread.run_sync(_compute_ao_cat)


def clear_computed_ao_cat() -> None:
    logger.info("Start AO-Cat clear cache")
    get_ao_cat.cache_clear()


async def recompute_ao_cat() -> None:
    logger.info("Start AO-Cat recompute")
    clear_computed_ao_cat()
    await get_ao_cat()


async def write_ao_cat(ttl: str) -> None:
    logger.info("Start AO-Cat write file")
    start = datetime.now()
    async with await open_file(
        f"{settings.json_data_dir}/ao-cat.ttl",
        mode="w",
        encoding="utf-8",
        newline="\n",
    ) as file:
        await file.write(ttl)
    logger.info(f"End write_ao_cat in {datetime.now() - start}")


async def export_ao_cat() -> None:
    logger.info("Start AO-Cat export")
    start = datetime.now()

    ttl = await get_ao_cat()
    await write_ao_cat(ttl)
    size = sizeof_fmt(os.lstat(f"{settings.json_data_dir}/ao-cat.ttl").st_size)
    logger.info(f"End export in {datetime.now() - start}: size = {size}")


if __name__ == "__main__":
    setup_logging()
    anyio.run(export_ao_cat)
