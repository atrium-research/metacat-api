from fastapi import APIRouter

from metacat_api.models.common import MappingRelation
from metacat_api.models.mapping import Mapping, VocabularyOverlap
from metacat_api.services import mappings as service

router = APIRouter(prefix="/mappings", tags=["Mappings"])


@router.get("", summary="Declared cross-vocabulary mappings")
def list_mappings(
    vocab_a: str | None = None,
    vocab_b: str | None = None,
    relation: MappingRelation | None = None,
) -> list[Mapping]:
    return service.list_mappings(vocab_a, vocab_b, relation)


@router.get(
    "/overlap",
    summary="Transversal overlap between two vocabularies",
)
def vocabulary_overlap(
    vocab_a: str,
    vocab_b: str,
) -> VocabularyOverlap:
    return service.vocabulary_overlap(vocab_a, vocab_b)
