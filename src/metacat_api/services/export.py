import logging
import urllib
from functools import lru_cache
from uuid import UUID

import anyio
import rdflib
from anyio import open_file
from rdflib import RDF, RDFS, SKOS, BNode, Graph, Literal, URIRef

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
from metacat_api.services.vocabularies import list_vocabularies

logger = logging.getLogger(__name__)


class ExportError(RuntimeError):
    pass


def _encode(term: str) -> str:
    if not term:
        return term
    return urllib.parse.quote_plus(term)


def _add_dimension(g: Graph, subject: URIRef, schema: URIRef, value: int | float):
    if not value:
        return

    dimension = BNode()
    g.add((dimension, RDF.type, AO_CAT.AO_Dimension))
    g.add((dimension, AO_CAT.has_value, Literal(value)))

    g.add((subject, schema, dimension))


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


def _add_facet_value(g: Graph, fv: FacetValue):
    fv_id = f"{fv.catalogue_id}_{fv.version_id}_{fv.facet}_{fv.value}"
    subject = ATRIUM_FACET_VALUE.term(_encode(fv_id))
    g.add((subject, RDF.type, ATRIUM.term("FacetValue")))
    g.add((subject, RDF.type, AO_CAT.AO_Entity))

    g.add((subject, ATRIUM.catalogue, ATRIUM_CATALOGUE.term(_encode(fv.catalogue_id))))
    cv_uri = ATRIUM_CATALOGUE_VERSION.term(_encode(f"{fv.catalogue_id}_{fv.version_id}"))
    g.add((subject, ATRIUM.catalogue_version, cv_uri))

    g.add((subject, CRM.P2_has_type, ATRIUM_FACET.term(_encode(fv.facet))))
    g.add((subject, AO_CAT.has_native_subject, Literal(fv.value)))

    _add_dimension(g, subject, AO_CAT.has_extent, fv.count)


rdflib.plugin.register(
    "custom_ttl",
    rdflib.plugin.Serializer,
    "metacat_api.models.export",
    "CustomTurtleSerializer",
)


def _compute_ao_cat() -> str:
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

    for fv in facet_values():
        _add_facet_value(g, fv)

    return g.serialize(format="custom_ttl", canon=True).strip()


_ao_cat: str | None = None


@lru_cache
def get_current_ao_cat() -> str:
    global _ao_cat
    if not _ao_cat:
        _ao_cat = _compute_ao_cat()
    return _ao_cat


def clear_compute_ao_cat() -> None:
    get_current_ao_cat.cache_clear()


async def export_ao_cat() -> None:
    async with await open_file(f"{settings.json_data_dir}/ao-cat.ttl", encoding="utf-8", mode="w") as file:
        await file.write(get_current_ao_cat())


if __name__ == "__main__":
    setup_logging()
    anyio.run(export_ao_cat)
