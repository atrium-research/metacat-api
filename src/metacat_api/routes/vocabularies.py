from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from metacat_api.models.common import ErrorResponse, Pagination
from metacat_api.models.vocabulary import Concept, Vocabulary
from metacat_api.services import vocabularies as service

router = APIRouter(prefix="/vocabularies", tags=["Vocabularies"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}


class PaginatedConcepts(BaseModel):
    pagination: Pagination = Field(description="Pagination window over the concept list.")
    items: list[Concept] = Field(description="Concepts in the requested window.")


def _require_vocabulary(vocabulary_id: str):
    vocabulary = service.get_vocabulary(vocabulary_id)
    if not vocabulary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown vocabulary '{vocabulary_id}'")
    return vocabulary


required_vocabulary = Annotated[Vocabulary, Depends(_require_vocabulary)]


@router.get("", summary="Vocabulary inventory")
def list_vocabularies() -> list[Vocabulary]:
    return service.list_vocabularies()


@router.get(
    "/{vocabulary_id}",
    responses=_NOT_FOUND,
    summary="Vocabulary detail",
    dependencies=[Depends(_require_vocabulary)],
)
def get_vocabulary(vocabulary_id: str, vocabulary: required_vocabulary) -> Vocabulary:
    return vocabulary


@router.get(
    "/{vocabulary_id}/concepts",
    responses=_NOT_FOUND,
    summary="Paginated concepts of a vocabulary",
    dependencies=[Depends(_require_vocabulary)],
)
def vocabulary_concepts(
    vocabulary_id: str,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
) -> PaginatedConcepts:
    items, total = service.vocabulary_concepts(vocabulary_id, offset, limit)
    return PaginatedConcepts(
        pagination=Pagination(offset=offset, limit=limit, total=total),
        items=items,
    )
