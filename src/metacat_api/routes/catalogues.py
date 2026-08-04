from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from metacat_api.models import Catalogue, ErrorResponse, FacetExposure, FacetExposureStatus, PivotFacet, Vocabulary
from metacat_api.services import catalogues as service

router = APIRouter(prefix="/catalogues", tags=["Catalogues"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}


def _require_catalogue(catalogue_id: str) -> Catalogue:
    catalogue = service.get_catalogue(catalogue_id)
    if catalogue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown catalogue '{catalogue_id}'")
    return catalogue


required_catalogue = Annotated[Catalogue, Depends(_require_catalogue)]


@router.get("", summary="List all catalogues")
def list_catalogues() -> list[Catalogue]:
    return service.list_catalogues()


@router.get(
    "/{catalogue_id}",
    responses=_NOT_FOUND,
    summary="Single catalogue detail",
    dependencies=[Depends(_require_catalogue)],
)
def get_catalogue(catalogue_id: str, catalogue: required_catalogue) -> Catalogue:
    return catalogue


@router.get(
    "/{catalogue_id}/facets",
    responses=_NOT_FOUND,
    summary="Facet exposure status for a catalogue",
    dependencies=[Depends(_require_catalogue)],
)
def catalogue_facets(catalogue_id: str) -> list[FacetExposure]:
    return service.catalogue_facets(catalogue_id)


@router.get(
    "/{catalogue_id}/vocabularies",
    responses=_NOT_FOUND,
    summary="Vocabularies used by a catalogue",
    dependencies=[Depends(_require_catalogue)],
)
def catalogue_vocabularies(catalogue_id: str) -> list[Vocabulary]:
    return service.catalogue_vocabularies(catalogue_id)


@router.get(
    "/{catalogue_id}/facet-coverage",
    responses=_NOT_FOUND,
    summary="Compact six-cell facet coverage for the Overview cards",
    dependencies=[Depends(_require_catalogue)],
)
def catalogue_facet_coverage(catalogue_id: str) -> dict[PivotFacet, FacetExposureStatus]:
    return service.facet_coverage(catalogue_id)


@router.get(
    "/{catalogue_id}/provenance",
    responses=_NOT_FOUND,
    summary="Lineage information for a catalogue",
    dependencies=[Depends(_require_catalogue)],
)
def catalogue_provenance(catalogue_id: str) -> dict:
    return service.provenance(catalogue_id)
