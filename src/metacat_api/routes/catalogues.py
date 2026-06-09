from fastapi import APIRouter, Depends, HTTPException

from metacat_api.datasources import get_datasource
from metacat_api.datasources.base import Datasource
from metacat_api.models.catalogue import Catalogue
from metacat_api.models.common import ErrorResponse, FacetExposureStatus, PivotFacet
from metacat_api.models.facet import FacetExposure
from metacat_api.models.vocabulary import Vocabulary
from metacat_api.services import catalogues as service

router = APIRouter(prefix="/catalogues", tags=["catalogues"])

_NOT_FOUND = {404: {"model": ErrorResponse}}


def _require(ds: Datasource, catalogue_id: str) -> Catalogue:
    catalogue = service.get_catalogue(ds, catalogue_id)
    if catalogue is None:
        raise HTTPException(status_code=404, detail=f"Unknown catalogue '{catalogue_id}'")
    return catalogue


@router.get("", response_model=list[Catalogue], summary="List all catalogues")
def list_catalogues(ds: Datasource = Depends(get_datasource)) -> list[Catalogue]:
    return service.list_catalogues(ds)


@router.get(
    "/{catalogue_id}",
    response_model=Catalogue,
    responses=_NOT_FOUND,
    summary="Single catalogue detail",
)
def get_catalogue(catalogue_id: str, ds: Datasource = Depends(get_datasource)) -> Catalogue:
    return _require(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/facets",
    response_model=list[FacetExposure],
    responses=_NOT_FOUND,
    summary="Facet exposure status for a catalogue",
)
def catalogue_facets(
    catalogue_id: str, ds: Datasource = Depends(get_datasource)
) -> list[FacetExposure]:
    _require(ds, catalogue_id)
    return service.catalogue_facets(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/vocabularies",
    response_model=list[Vocabulary],
    responses=_NOT_FOUND,
    summary="Vocabularies used by a catalogue",
)
def catalogue_vocabularies(
    catalogue_id: str, ds: Datasource = Depends(get_datasource)
) -> list[Vocabulary]:
    _require(ds, catalogue_id)
    return service.catalogue_vocabularies(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/facet-coverage",
    response_model=dict[PivotFacet, FacetExposureStatus],
    responses=_NOT_FOUND,
    summary="Compact six-cell facet coverage for the Overview cards",
)
def catalogue_facet_coverage(
    catalogue_id: str, ds: Datasource = Depends(get_datasource)
) -> dict[PivotFacet, FacetExposureStatus]:
    _require(ds, catalogue_id)
    return service.facet_coverage(ds, catalogue_id)


@router.get(
    "/{catalogue_id}/provenance",
    responses=_NOT_FOUND,
    summary="Lineage information for a catalogue",
)
def catalogue_provenance(catalogue_id: str, ds: Datasource = Depends(get_datasource)) -> dict:
    _require(ds, catalogue_id)
    return service.provenance(ds, catalogue_id)
