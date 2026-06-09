from metacat_api.datasources.base import Datasource
from metacat_api.models.catalogue import Catalogue
from metacat_api.models.common import FacetExposureStatus, PivotFacet
from metacat_api.models.facet import FacetExposure
from metacat_api.models.vocabulary import Vocabulary


def list_catalogues(ds: Datasource) -> list[Catalogue]:
    return ds.catalogues()


def get_catalogue(ds: Datasource, catalogue_id: str) -> Catalogue | None:
    return next((c for c in ds.catalogues() if c.id == catalogue_id), None)


def catalogue_facets(ds: Datasource, catalogue_id: str) -> list[FacetExposure]:
    return [e for e in ds.facet_exposures() if e.catalogue_id == catalogue_id]


def catalogue_vocabularies(ds: Datasource, catalogue_id: str) -> list[Vocabulary]:
    return [v for v in ds.vocabularies() if catalogue_id in v.used_by_catalogues]


def facet_coverage(ds: Datasource, catalogue_id: str) -> dict[PivotFacet, FacetExposureStatus]:
    return {e.facet: e.status for e in catalogue_facets(ds, catalogue_id)}


def provenance(ds: Datasource, catalogue_id: str) -> dict:
    catalogue = get_catalogue(ds, catalogue_id)
    if catalogue is None:
        return {}
    return {
        "catalogue_id": catalogue.id,
        "source_catalogue_url": str(catalogue.url),
        "datastore": "metacat-data (timestamped JSON) and GraphDB (AO-Cat model)",
        "last_harvest_at": catalogue.last_harvest_at,
        "harvest_status": catalogue.harvest_status,
    }
