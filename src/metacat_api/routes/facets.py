from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from metacat_api.datasources import datasource_dep
from metacat_api.models.common import PivotFacet
from metacat_api.models.facet import FacetComparison, FacetTimeseriesPoint, FacetValue
from metacat_api.services import facets as service

router = APIRouter(prefix="/facets", tags=["Facets"])

_catalogues_query = Annotated[
    str | None,
    Query(description="Comma-separated catalogue identifiers to restrict the result."),
]


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
    ds: datasource_dep,
    facet: PivotFacet,
    catalogues: _catalogues_query = None,
    date_from: Annotated[datetime | None, Query(alias="from")] = None,
    date_to: Annotated[datetime | None, Query(alias="to")] = None,
) -> list[FacetValue]:
    return service.facet_values(ds, facet, _parse_catalogues(catalogues), date_from, date_to)


@router.get(
    "/{facet}/compare",
    summary="Transversal side-by-side comparison across catalogues",
)
def facet_compare(
    ds: datasource_dep,
    facet: PivotFacet,
    catalogues: _catalogues_query = None,
) -> FacetComparison:
    return service.facet_compare(ds, facet, _parse_catalogues(catalogues))


@router.get(
    "/{facet}/timeseries",
    summary="Evolution of a facet over time",
)
def facet_timeseries(
    ds: datasource_dep,
    facet: PivotFacet,
    catalogues: _catalogues_query = None,
    date_from: Annotated[datetime | None, Query(alias="from")] = None,
    date_to: Annotated[datetime | None, Query(alias="to")] = None,
) -> list[FacetTimeseriesPoint]:
    return service.facet_timeseries(ds, facet, _parse_catalogues(catalogues), date_from, date_to)
