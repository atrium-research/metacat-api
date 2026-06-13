from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from metacat_api.datasources import get_datasource
from metacat_api.datasources.base import Datasource
from metacat_api.models.common import ErrorResponse, Pagination
from metacat_api.models.vocabulary import Concept, Vocabulary
from metacat_api.services import vocabularies as service

router = APIRouter(prefix="/vocabularies", tags=["vocabularies"])

_NOT_FOUND = {404: {"model": ErrorResponse}}


class PaginatedConcepts(BaseModel):
    pagination: Pagination = Field(description="Pagination window over the concept list.")
    items: list[Concept] = Field(description="Concepts in the requested window.")


@router.get("", response_model=list[Vocabulary], summary="Vocabulary inventory")
def list_vocabularies(ds: Datasource = Depends(get_datasource)) -> list[Vocabulary]:
    return service.list_vocabularies(ds)


@router.get(
    "/{vocabulary_id}",
    response_model=Vocabulary,
    responses=_NOT_FOUND,
    summary="Vocabulary detail",
)
def get_vocabulary(vocabulary_id: str, ds: Datasource = Depends(get_datasource)) -> Vocabulary:
    vocabulary = service.get_vocabulary(ds, vocabulary_id)
    if vocabulary is None:
        raise HTTPException(status_code=404, detail=f"Unknown vocabulary '{vocabulary_id}'")
    return vocabulary


@router.get(
    "/{vocabulary_id}/concepts",
    response_model=PaginatedConcepts,
    responses=_NOT_FOUND,
    summary="Paginated concepts of a vocabulary",
)
def vocabulary_concepts(
    vocabulary_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    ds: Datasource = Depends(get_datasource),
) -> PaginatedConcepts:
    if service.get_vocabulary(ds, vocabulary_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown vocabulary '{vocabulary_id}'")
    items, total = service.vocabulary_concepts(ds, vocabulary_id, offset, limit)
    return PaginatedConcepts(
        pagination=Pagination(offset=offset, limit=limit, total=total),
        items=items,
    )
