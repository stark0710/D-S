"""
Unit tests for KnowledgeRepository.
"""

from pathlib import Path
import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.engineering_parameter import EngineeringParameter
from backend.models.mission_domain import MissionDomain
from backend.knowledge.knowledge_repository import (
    KnowledgeRepository,
    DuplicateEntityIDError,
    EntityNotFoundError,
)
from backend.knowledge.loader.filesystem_loader import FilesystemRepositoryLoader
from backend.knowledge.repository_validator import RepositoryValidator
from backend.knowledge.parser.document_reader import DocumentReader
from backend.knowledge.parser.front_matter_parser import FrontMatterParser
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser
from backend.knowledge.parser.document_parsing_pipeline import DocumentParsingPipeline
from backend.knowledge.builders.engineering_parameter_builder import EngineeringParameterBuilder
from backend.knowledge.builders.builder_registry import BuilderRegistry
from backend.knowledge.builders.entity_construction_pipeline import EntityConstructionPipeline
from backend.knowledge.knowledge_engine import KnowledgeEngine


@pytest.fixture
def sample_entities() -> list[KnowledgeEntity]:
    return [
        EngineeringParameter(
            id="EP-001",
            name="Wing Span",
            description="Total wing length",
            library="EPL-001",
            parameter_group="Geometry",
            engineering_classification="Physical",
            unit="m"
        ),
        EngineeringParameter(
            id="EP-002",
            name="Cruise Speed",
            description="Operational cruise speed",
            library="EPL-001",
            parameter_group="Performance",
            engineering_classification="Performance",
            unit="m/s"
        ),
        MissionDomain(
            id="MD-001",
            name="Agriculture",
            description="Agricultural UAS operations",
            category_ids=["MC-001"]
        ),
    ]


def test_knowledge_repository_lookups(sample_entities: list[KnowledgeEntity]):
    """Verify get_all, get_by_id, has_entity, get_by_type, count, and entity_types."""
    repo = KnowledgeRepository(sample_entities)

    assert repo.count() == 3
    assert len(repo.get_all()) == 3

    # ID lookup
    assert repo.has_entity("EP-001")
    assert repo.has_entity("MD-001")
    assert not repo.has_entity("NONEXISTENT")

    ep1 = repo.get_by_id("EP-001")
    assert ep1.name == "Wing Span"

    md1 = repo.get_by_id("MD-001")
    assert md1.name == "Agriculture"

    # Type lookup
    eps = repo.get_by_type(EngineeringParameter)
    assert len(eps) == 2
    assert {e.id for e in eps} == {"EP-001", "EP-002"}

    mds = repo.get_by_type(MissionDomain)
    assert len(mds) == 1
    assert mds[0].id == "MD-001"

    all_ke = repo.get_by_type(KnowledgeEntity)
    assert len(all_ke) == 3

    # Entity types list
    types = repo.entity_types()
    assert EngineeringParameter in types
    assert MissionDomain in types


def test_entity_not_found_error(sample_entities: list[KnowledgeEntity]):
    """Verify EntityNotFoundError is raised when entity ID does not exist."""
    repo = KnowledgeRepository(sample_entities)

    with pytest.raises(EntityNotFoundError):
        repo.get_by_id("EP-999")


def test_duplicate_entity_id_error():
    """Verify DuplicateEntityIDError is raised during initialization if IDs collide."""
    e1 = KnowledgeEntity(id="DUPLICATE-ID", name="Entity 1", description="First")
    e2 = KnowledgeEntity(id="DUPLICATE-ID", name="Entity 2", description="Second")

    with pytest.raises(DuplicateEntityIDError):
        KnowledgeRepository([e1, e2])


def test_empty_knowledge_repository():
    """Verify behavior of empty repository."""
    repo = KnowledgeRepository()

    assert repo.count() == 0
    assert repo.get_all() == []
    assert repo.get_by_type(EngineeringParameter) == []
    assert repo.entity_types() == []
    assert not repo.has_entity("EP-001")


def test_workspace_repository_integration():
    """Verify loading workspace entities into KnowledgeRepository."""
    workspace_docs = Path("docs/engineering_knowledge_base")
    if workspace_docs.exists():
        loader = FilesystemRepositoryLoader(workspace_docs)
        parse_pipeline = DocumentParsingPipeline(
            reader=DocumentReader(),
            front_matter_parser=FrontMatterParser(),
            section_parser=MarkdownSectionParser()
        )
        registry = BuilderRegistry()
        registry.register("engineering_parameter", EngineeringParameterBuilder())
        construct_pipeline = EntityConstructionPipeline(registry=registry)

        engine = KnowledgeEngine(
            loader=loader,
            validator_factory=RepositoryValidator,
            parse_pipeline=parse_pipeline,
            construct_pipeline=construct_pipeline
        )

        entities = engine.load_repository()
        repo = KnowledgeRepository(entities)

        assert repo.count() == len(entities)
        assert len(repo.get_by_type(EngineeringParameter)) > 0
