from fastapi import APIRouter, Query

from metacat_api.datasources import datasource_dep
from metacat_api.models.common import MappingRelation
from metacat_api.models.mapping import Mapping, VocabularyOverlap
from metacat_api.services import mappings as service

router = APIRouter(prefix="/mappings", tags=["Mappings"])


@router.get("", summary="Declared cross-vocabulary mappings")
def list_mappings(
    ds: datasource_dep,
    vocab_a: str | None = Query(default=None),
    vocab_b: str | None = Query(default=None),
    relation: MappingRelation | None = Query(default=None),
) -> list[Mapping]:
    return service.list_mappings(ds, vocab_a, vocab_b, relation)


@router.get(
    "/overlap",
    summary="Transversal overlap between two vocabularies",
)
def vocabulary_overlap(
    ds: datasource_dep,
    vocab_a: str = Query(),
    vocab_b: str = Query(),
) -> VocabularyOverlap:
    return service.vocabulary_overlap(ds, vocab_a, vocab_b)
