from fastapi import APIRouter, HTTPException

from metacat_api.datasources import datasource_dep
from metacat_api.datasources.base import Datasource
from metacat_api.models.catalogue import Catalogue
from metacat_api.models.common import ErrorResponse, FacetExposureStatus, PivotFacet
from metacat_api.models.facet import FacetExposure
from metacat_api.models.vocabulary import Vocabulary
from metacat_api.services import catalogues as service

router = APIRouter(prefix="/catalogues", tags=["Catalogues"])

_NOT_FOUND = {404: {"model": ErrorResponse}}


def _require(ds: Datasource, catalogue_id: str) -> Catalogue:
    catalogue = service.get_catalogue(ds, catalogue_id)
    if catalogue is None:
        raise HTTPException(status_code=404, detail=f"Unknown catalogue '{catalogue_id}'")
    return catalogue


@router.get("", summary="List all catalogues")
def list_catalogues(ds: datasource_dep) -> list[Catalogue]:
    return service.list_catalogues(ds)


@router.get(
    "/{catalogue_id}",
    responses=_NOT_FOUND,
    summary="Single catalogue detail",
)
def get_catalogue(catalogue_id: str, ds: datasource_dep) -> Catalogue:
    return _require(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/facets",
    responses=_NOT_FOUND,
    summary="Facet exposure status for a catalogue",
)
def catalogue_facets(catalogue_id: str, ds: datasource_dep) -> list[FacetExposure]:
    _require(ds, catalogue_id)
    return service.catalogue_facets(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/vocabularies",
    responses=_NOT_FOUND,
    summary="Vocabularies used by a catalogue",
)
def catalogue_vocabularies(catalogue_id: str, ds: datasource_dep) -> list[Vocabulary]:
    _require(ds, catalogue_id)
    return service.catalogue_vocabularies(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/facet-coverage",
    responses=_NOT_FOUND,
    summary="Compact six-cell facet coverage for the Overview cards",
)
def catalogue_facet_coverage(catalogue_id: str, ds: datasource_dep) -> dict[PivotFacet, FacetExposureStatus]:
    _require(ds, catalogue_id)
    return service.facet_coverage(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/provenance",
    responses=_NOT_FOUND,
    summary="Lineage information for a catalogue",
)
def catalogue_provenance(catalogue_id: str, ds: datasource_dep) -> dict:
    _require(ds, catalogue_id)
    return service.provenance(ds, catalogue_id)
