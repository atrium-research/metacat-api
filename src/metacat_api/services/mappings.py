from metacat_api.datasources.base import Datasource
from metacat_api.models.common import MappingRelation
from metacat_api.models.mapping import Mapping, VocabularyOverlap


def _scheme_of(ds: Datasource, vocabulary_id: str) -> str | None:
    vocabulary = next((v for v in ds.vocabularies() if v.id == vocabulary_id), None)
    return vocabulary.name if vocabulary else None


def list_mappings(
    ds: Datasource,
    vocab_a: str | None = None,
    vocab_b: str | None = None,
    relation: MappingRelation | None = None,
) -> list[Mapping]:
    scheme_a = _scheme_of(ds, vocab_a) if vocab_a else None
    scheme_b = _scheme_of(ds, vocab_b) if vocab_b else None

    result = []
    for mapping in ds.mappings():
        schemes = {mapping.source_concept.scheme, mapping.target_concept.scheme}
        if scheme_a and scheme_a not in schemes:
            continue
        if scheme_b and scheme_b not in schemes:
            continue
        if relation and mapping.relation != relation:
            continue
        result.append(mapping)
    return result


def vocabulary_overlap(ds: Datasource, vocab_a: str, vocab_b: str) -> VocabularyOverlap:
    scheme_a = _scheme_of(ds, vocab_a)
    scheme_b = _scheme_of(ds, vocab_b)

    relations: dict[MappingRelation, int] = {}
    shared = 0
    for mapping in ds.mappings():
        schemes = {mapping.source_concept.scheme, mapping.target_concept.scheme}
        if scheme_a in schemes and scheme_b in schemes:
            shared += 1
            relations[mapping.relation] = relations.get(mapping.relation, 0) + 1

    vocabularies = {v.id: v for v in ds.vocabularies()}
    total_a = vocabularies[vocab_a].concepts_count if vocab_a in vocabularies else 0
    total_b = vocabularies[vocab_b].concepts_count if vocab_b in vocabularies else 0

    return VocabularyOverlap(
        vocab_a=vocab_a,
        vocab_b=vocab_b,
        shared_concepts=shared,
        total_a=total_a,
        total_b=total_b,
        mapping_relations=relations,
    )
