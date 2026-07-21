from datetime import datetime

from fastapi import APIRouter, Depends, Query

from metacat_api.datasources import get_datasource
from metacat_api.datasources.base import Datasource
from metacat_api.models.common import PivotFacet
from metacat_api.models.facet import FacetComparison, FacetTimeseriesPoint, FacetValue
from metacat_api.services import facets as service

router = APIRouter(prefix="/facets", tags=["facets"])

_CATALOGUES_QUERY = Query(default=None, description="Comma-separated catalogue identifiers to restrict the result.")


def _parse_catalogues(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    return [item.strip() for item in raw.split(",") if item.strip()]


@router.get("", summary="List the six pivot facets")
def list_facets() -> list[str]:
    return service.list_facets()


@router.get(
    "/{facet}/values",
    summary="Facet values with counts and timestamps",
)
def facet_values(
    facet: PivotFacet,
    catalogues: str | None = _CATALOGUES_QUERY,
    date_from: datetime | None = Query(default=None, alias="from"),
    date_to: datetime | None = Query(default=None, alias="to"),
    ds: Datasource = Depends(get_datasource),
) -> list[FacetValue]:
    return service.facet_values(ds, facet, _parse_catalogues(catalogues), date_from, date_to)


@router.get(
    "/{facet}/compare",
    summary="Transversal side-by-side comparison across catalogues",
)
def facet_compare(
    facet: PivotFacet,
    catalogues: str | None = _CATALOGUES_QUERY,
    ds: Datasource = Depends(get_datasource),
) -> FacetComparison:
    return service.facet_compare(ds, facet, _parse_catalogues(catalogues))


@router.get(
    "/{facet}/timeseries",
    summary="Evolution of a facet over time",
)
def facet_timeseries(
    facet: PivotFacet,
    catalogues: str | None = _CATALOGUES_QUERY,
    date_from: datetime | None = Query(default=None, alias="from"),
    date_to: datetime | None = Query(default=None, alias="to"),
    ds: Datasource = Depends(get_datasource),
) -> list[FacetTimeseriesPoint]:
    return service.facet_timeseries(ds, facet, _parse_catalogues(catalogues), date_from, date_to)
