from pydantic import BaseModel, Field

from metacat_api.models.common import MappingRelation
from metacat_api.models.vocabulary import ConceptRef


class Mapping(BaseModel):
    source_concept: ConceptRef = Field(description="Concept the mapping starts from.")
    target_concept: ConceptRef = Field(description="Concept the mapping points to.")
    relation: MappingRelation = Field(description="SKOS mapping relation between the concepts.")
    authority: str = Field(description="Source that declared the mapping.")


class VocabularyOverlap(BaseModel):
    vocab_a: str = Field(description="First vocabulary identifier.")
    vocab_b: str = Field(description="Second vocabulary identifier.")
    shared_concepts: int = Field(description="Number of concepts mapped between the two.")
    total_a: int = Field(description="Total concepts in the first vocabulary.")
    total_b: int = Field(description="Total concepts in the second vocabulary.")
    mapping_relations: dict[MappingRelation, int] = Field(description="Count of shared concepts per mapping relation.")
