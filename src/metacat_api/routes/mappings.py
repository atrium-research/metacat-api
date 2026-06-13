from fastapi import APIRouter, Depends, Query

from metacat_api.datasources import get_datasource
from metacat_api.datasources.base import Datasource
from metacat_api.models.common import MappingRelation
from metacat_api.models.mapping import Mapping, VocabularyOverlap
from metacat_api.services import mappings as service

router = APIRouter(prefix="/mappings", tags=["mappings"])


@router.get("", response_model=list[Mapping], summary="Declared cross-vocabulary mappings")
def list_mappings(
    vocab_a: str | None = Query(default=None),
    vocab_b: str | None = Query(default=None),
    relation: MappingRelation | None = Query(default=None),
    ds: Datasource = Depends(get_datasource),
) -> list[Mapping]:
    return service.list_mappings(ds, vocab_a, vocab_b, relation)


@router.get(
    "/overlap",
    response_model=VocabularyOverlap,
    summary="Transversal overlap between two vocabularies",
)
def vocabulary_overlap(
    vocab_a: str = Query(),
    vocab_b: str = Query(),
    ds: Datasource = Depends(get_datasource),
) -> VocabularyOverlap:
    return service.vocabulary_overlap(ds, vocab_a, vocab_b)
