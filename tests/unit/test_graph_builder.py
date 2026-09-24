"""
Unit tests for GraphBuilder.
"""

from pathlib import Path
import pytest
from backend.models.engineering_parameter import EngineeringParameter
from backend.models.mission_domain import MissionDomain
from backend.knowledge.knowledge_repository import KnowledgeRepository
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_builder import GraphBuilder, EmptyRepositoryError
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


def test_graph_builder_success():
    """Verify GraphBuilder populates KnowledgeGraph with nodes from KnowledgeRepository."""
    e1 = EngineeringParameter(
        id="EP-001",
        name="Wing Span",
        description="Wing span",
        library="EPL-001",
        parameter_group="Geometry",
        engineering_classification="Physical"
    )
    e2 = MissionDomain(id="MD-001", name="Agriculture", description="Ag domain", category_ids=[])

    repo = KnowledgeRepository([e1, e2])
    builder = GraphBuilder(repository=repo)
    graph = builder.build()

    assert isinstance(graph, KnowledgeGraph)
    assert graph.entity_count() == 2
    assert graph.has_entity("EP-001")
    assert graph.has_entity("MD-001")
    assert graph.get_entity("EP-001") == e1
    assert graph.get_entity("MD-001") == e2


def test_empty_repository_raises_error():
    """Verify EmptyRepositoryError is raised when building graph from empty repository."""
    repo = KnowledgeRepository([])
    builder = GraphBuilder(repository=repo)

    with pytest.raises(EmptyRepositoryError):
        builder.build()


def test_workspace_graph_builder_integration():
    """Integration test building KnowledgeGraph from actual workspace repository."""
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

        builder = GraphBuilder(repository=repo)
        graph = builder.build()

        assert graph.entity_count() == repo.count()
        assert graph.has_entity("MP-007-008") or graph.entity_count() > 0
