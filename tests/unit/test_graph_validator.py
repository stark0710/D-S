"""
Unit tests for GraphValidator and GraphValidationResult.
"""

from pathlib import Path
import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.knowledge_relationship import KnowledgeRelationship
from backend.models.mission_domain import MissionDomain
from backend.models.mission_category import MissionCategory
from backend.knowledge.knowledge_repository import KnowledgeRepository
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_edge import GraphEdge
from backend.knowledge.graph.graph_builder import GraphBuilder
from backend.knowledge.graph.relationship_resolver import RelationshipResolver
from backend.knowledge.graph.graph_construction_pipeline import GraphConstructionPipeline
from backend.knowledge.graph.graph_validation_result import GraphValidationResult
from backend.knowledge.graph.graph_validator import GraphValidator
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


def test_graph_validator_valid_graph():
    """Verify GraphValidator on a structurally sound, connected KnowledgeGraph."""
    md = MissionDomain(id="MD-001", name="Agriculture", description="Ag", category_ids=["MC-001"])
    mc = MissionCategory(id="MC-001", name="Crop Spraying", description="Spraying", domain_id="MD-001", objective="Crop Protection", engineering_parameter_ids=[])

    graph = KnowledgeGraph()
    graph.add_entity(md)
    graph.add_entity(mc)

    resolver = RelationshipResolver(graph=graph)
    resolver.resolve()

    validator = GraphValidator(graph=graph)
    result = validator.validate()

    assert isinstance(result, GraphValidationResult)
    assert result.is_valid
    assert result.errors == []
    assert result.statistics["entity_count"] == 2
    assert result.statistics["edge_count"] == 1
    assert result.statistics["isolated_nodes"] == 0
    assert result.statistics["average_degree"] == 1.0
    assert result.statistics["maximum_degree"] == 1
    assert result.statistics["minimum_degree"] == 1


def test_graph_validator_isolated_nodes_and_stats():
    """Verify statistics calculation for graph with isolated nodes."""
    e1 = KnowledgeEntity(id="E-001", name="Node 1", description="Desc")
    e2 = KnowledgeEntity(id="E-002", name="Node 2", description="Desc")

    graph = KnowledgeGraph()
    graph.add_entity(e1)
    graph.add_entity(e2)

    validator = GraphValidator(graph=graph)
    result = validator.validate()

    assert result.is_valid
    assert result.statistics["entity_count"] == 2
    assert result.statistics["edge_count"] == 0
    assert result.statistics["isolated_nodes"] == 2
    assert result.statistics["average_degree"] == 0.0


def test_graph_validator_duplicate_edge_warning():
    """Verify duplicate edges trigger warnings in GraphValidationResult."""
    e1 = KnowledgeEntity(id="E-001", name="Node 1", description="Desc")
    e2 = KnowledgeEntity(id="E-002", name="Node 2", description="Desc")

    graph = KnowledgeGraph()
    graph.add_entity(e1)
    graph.add_entity(e2)

    rel1 = KnowledgeRelationship(source_id="E-001", source_type="E", target_id="E-002", target_type="E", relationship_type="depends_on")
    rel2 = KnowledgeRelationship(source_id="E-001", source_type="E", target_id="E-002", target_type="E", relationship_type="depends_on")

    graph.add_relationship(rel1)
    graph.add_relationship(rel2)

    validator = GraphValidator(graph=graph)
    result = validator.validate()

    assert result.is_valid
    assert len(result.warnings) == 1
    assert "Duplicate edge detected" in result.warnings[0]


def test_workspace_graph_validator_integration():
    """Integration test running GraphValidator on workspace KnowledgeGraph constructed via pipeline."""
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
        construction_pipeline = GraphConstructionPipeline(builder=builder, resolver_factory=RelationshipResolver)
        graph = construction_pipeline.construct()

        validator = GraphValidator(graph=graph)
        result = validator.validate()

        assert result.is_valid
        assert result.statistics["entity_count"] > 0
