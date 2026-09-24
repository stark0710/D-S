"""
Unit tests for EntityBuilder abstract base class.
"""

from pathlib import Path
import pytest
from backend.knowledge.builders.entity_builder import EntityBuilder
from backend.models.repository_document import RepositoryDocument
from backend.models.parsed_document import ParsedDocument
from backend.models.knowledge_entity import KnowledgeEntity


def test_cannot_instantiate_abstract_entity_builder():
    """Verify EntityBuilder cannot be instantiated directly."""
    with pytest.raises(TypeError):
        EntityBuilder()


def test_concrete_entity_builder_subclass_implementation():
    """Verify concrete subclass can implement build method contract."""
    class DummyEntityBuilder(EntityBuilder):
        def build(self, document: ParsedDocument) -> KnowledgeEntity:
            return KnowledgeEntity(
                id="KE-BUILD-001",
                name="Built Entity",
                description="Entity built from ParsedDocument"
            )

    repo_doc = RepositoryDocument(
        path=Path("/tmp/test.md"),
        relative_path=Path("test.md"),
        file_name="test.md",
        document_type="test"
    )
    parsed_doc = ParsedDocument(repository_document=repo_doc)

    builder = DummyEntityBuilder()
    entity = builder.build(parsed_doc)

    assert isinstance(builder, EntityBuilder)
    assert isinstance(entity, KnowledgeEntity)
    assert entity.id == "KE-BUILD-001"
    assert entity.name == "Built Entity"
