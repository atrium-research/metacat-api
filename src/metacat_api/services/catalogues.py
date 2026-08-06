from metacat_api.datasources.store import store
from metacat_api.models import Catalogue, FacetExposure, FacetExposureStatus, PivotFacet, Vocabulary


def list_catalogues() -> list[Catalogue]:
    return store.catalogues


def get_catalogue(catalogue_id: str) -> Catalogue | None:
    return next((c for c in store.catalogues if c.id == catalogue_id), None)


def catalogue_facets(catalogue_id: str) -> list[FacetExposure]:
    return [e for e in store.facet_exposures if e.catalogue_id == catalogue_id]


def catalogue_vocabularies(catalogue_id: str) -> list[Vocabulary]:
    return [v for v in store.vocabularies if catalogue_id in v.used_by_catalogues]


def facet_coverage(catalogue_id: str) -> dict[PivotFacet, FacetExposureStatus]:
    return {e.facet: e.status for e in catalogue_facets(catalogue_id)}


def provenance(catalogue_id: str) -> dict:
    catalogue = get_catalogue(catalogue_id)
    if catalogue is None:
        return {}
    return {
        "catalogue_id": catalogue.id,
        "source_catalogue_url": str(catalogue.url),
        "datastore": "metacat-data (timestamped JSON) and GraphDB (AO-Cat model)",
        "last_harvest_at": catalogue.last_harvest_at,
        "harvest_status": catalogue.harvest_status,
    }
