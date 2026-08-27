from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from metacat_api.models.common import ErrorResponse
from metacat_api.models.vocabulary import Vocabulary
from metacat_api.services import vocabularies as service

router = APIRouter(prefix="/vocabularies", tags=["Vocabularies"])

_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}}


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

