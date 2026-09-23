"""
Unit tests for GraphConstructionPipeline.
"""

from pathlib import Path
import pytest
from backend.models.mission_domain import MissionDomain
from backend.models.mission_category import MissionCategory
from backend.knowledge.knowledge_repository import KnowledgeRepository
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_builder import GraphBuilder, EmptyRepositoryError
from backend.knowledge.graph.relationship_resolver import RelationshipResolver, UnresolvedRelationshipError
from backend.knowledge.graph.graph_construction_pipeline import GraphConstructionPipeline
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


def test_graph_construction_pipeline_success():
    """Verify GraphConstructionPipeline orchestrates node creation and relationship resolution."""
    md = MissionDomain(id="MD-001", name="Agriculture", description="Ag", category_ids=["MC-001"])
    mc = MissionCategory(id="MC-001", name="Crop Spraying", description="Spraying", domain_id="MD-001", objective="Protect Crops", engineering_parameter_ids=[])

    repo = KnowledgeRepository([md, mc])
    builder = GraphBuilder(repository=repo)
    pipeline = GraphConstructionPipeline(builder=builder, resolver_factory=RelationshipResolver)

    graph = pipeline.construct()

    assert isinstance(graph, KnowledgeGraph)
    assert graph.entity_count() == 2
    assert graph.relationship_count() == 1

    node_md = graph.get_node("MD-001")
    assert len(node_md.outgoing_edges) == 1
    assert node_md.outgoing_edges[0].target_id == "MC-001"


def test_builder_failure_propagates():
    """Verify error propagation when GraphBuilder fails."""
    repo = KnowledgeRepository([])  # Empty repository
    builder = GraphBuilder(repository=repo)
    pipeline = GraphConstructionPipeline(builder=builder, resolver_factory=RelationshipResolver)

    with pytest.raises(EmptyRepositoryError):
        pipeline.construct()


def test_workspace_graph_construction_pipeline_integration():
    """Integration test constructing KnowledgeGraph from workspace repository entities."""
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
        pipeline = GraphConstructionPipeline(builder=builder, resolver_factory=RelationshipResolver)

        graph = pipeline.construct()

        assert graph.entity_count() == repo.count()
        assert isinstance(graph, KnowledgeGraph)
