from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from metacat_api.datasources import datasource_dep
from metacat_api.models.common import ErrorResponse, Pagination
from metacat_api.models.vocabulary import Concept, Vocabulary
from metacat_api.services import vocabularies as service

router = APIRouter(prefix="/vocabularies", tags=["Vocabularies"])

_NOT_FOUND = {404: {"model": ErrorResponse}}


class PaginatedConcepts(BaseModel):
    pagination: Pagination = Field(description="Pagination window over the concept list.")
    items: list[Concept] = Field(description="Concepts in the requested window.")


@router.get("", summary="Vocabulary inventory")
def list_vocabularies(ds: datasource_dep) -> list[Vocabulary]:
    return service.list_vocabularies(ds)


@router.get(
    "/{vocabulary_id}",
    responses=_NOT_FOUND,
    summary="Vocabulary detail",
)
def get_vocabulary(vocabulary_id: str, ds: datasource_dep) -> Vocabulary:
    vocabulary = service.get_vocabulary(ds, vocabulary_id)
    if vocabulary is None:
        raise HTTPException(status_code=404, detail=f"Unknown vocabulary '{vocabulary_id}'")
    return vocabulary


@router.get(
    "/{vocabulary_id}/concepts",
    responses=_NOT_FOUND,
    summary="Paginated concepts of a vocabulary",
)
def vocabulary_concepts(
    ds: datasource_dep,
    vocabulary_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
) -> PaginatedConcepts:
    if service.get_vocabulary(ds, vocabulary_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown vocabulary '{vocabulary_id}'")
    items, total = service.vocabulary_concepts(ds, vocabulary_id, offset, limit)
    return PaginatedConcepts(
        pagination=Pagination(offset=offset, limit=limit, total=total),
        items=items,
    )
