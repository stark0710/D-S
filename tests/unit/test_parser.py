"""
Unit tests for Parser abstract base class.
"""

from pathlib import Path
import pytest
from backend.knowledge.parser.parser import Parser
from backend.models.repository_document import RepositoryDocument
from backend.models.knowledge_entity import KnowledgeEntity


def test_cannot_instantiate_abstract_parser():
    """Verify Parser abstract base class cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Parser()


def test_concrete_parser_subclass_implementation():
    """Verify concrete subclass can implement parse method contract."""
    class DummyParser(Parser):
        def parse(self, document: RepositoryDocument) -> KnowledgeEntity:
            return KnowledgeEntity(
                id="KE-000",
                name="Dummy Entity",
                description="Dummy Description"
            )

    doc = RepositoryDocument(
        path=Path("/tmp/dummy.md"),
        relative_path=Path("dummy.md"),
        file_name="dummy.md",
        document_type="dummy"
    )

    parser = DummyParser()
    entity = parser.parse(doc)

    assert isinstance(parser, Parser)
    assert isinstance(entity, KnowledgeEntity)
    assert entity.id == "KE-000"
    assert entity.name == "Dummy Entity"
