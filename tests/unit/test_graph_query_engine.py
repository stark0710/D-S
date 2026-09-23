"""
Unit tests for GraphQueryEngine.
"""

from pathlib import Path
import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.mission_domain import MissionDomain
from backend.models.mission_category import MissionCategory
from backend.models.engineering_parameter import EngineeringParameter
from backend.knowledge.knowledge_repository import KnowledgeRepository
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_edge import GraphEdge
from backend.knowledge.graph.graph_node import GraphNode
from backend.knowledge.graph.graph_builder import GraphBuilder
from backend.knowledge.graph.relationship_resolver import RelationshipResolver
from backend.knowledge.graph.graph_construction_pipeline import GraphConstructionPipeline
from backend.knowledge.graph.graph_indexer import GraphIndexer
from backend.knowledge.graph.graph_traversal_service import GraphTraversalService
from backend.knowledge.graph.graph_query_engine import (
    GraphQueryEngine,
    QueryEntityNotFoundError,
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


def test_graph_query_engine_methods():
    """Verify get_node, get_entity, get_entities_by_type, get_neighbors, find_related, path_exists, and reachable_entities."""
    md = MissionDomain(id="MD-001", name="Agriculture", description="Ag", category_ids=["MC-001"])
    mc = MissionCategory(id="MC-001", name="Crop Spraying", description="Spraying", domain_id="MD-001", objective="Protect Crops", engineering_parameter_ids=[])

    graph = KnowledgeGraph()
    graph.add_entity(md)
    graph.add_entity(mc)

    resolver = RelationshipResolver(graph=graph)
    resolver.resolve()

    indexer = GraphIndexer(graph=graph)
    traversal = GraphTraversalService(graph=graph, indexer=indexer)
    query_engine = GraphQueryEngine(indexer=indexer, traversal_service=traversal)

    # 1. Node & Entity lookups
    node_md = query_engine.get_node("MD-001")
    assert isinstance(node_md, GraphNode)

    entity_md = query_engine.get_entity("MD-001")
    assert isinstance(entity_md, MissionDomain)
    assert entity_md.id == "MD-001"

    # 2. Lookup by type
    domains = query_engine.get_entities_by_type(MissionDomain)
    assert len(domains) == 1
    assert domains[0].id == "MD-001"

    # 3. Neighbors lookup
    neighbors = query_engine.get_neighbors("MD-001")
    assert len(neighbors) == 1
    assert neighbors[0].id == "MC-001"

    # 4. Find related with relationship_type filter
    related_contains = query_engine.find_related("MD-001", relationship_type="contains")
    assert len(related_contains) == 1
    assert related_contains[0].id == "MC-001"

    related_none = query_engine.find_related("MD-001", relationship_type="nonexistent")
    assert related_none == []

    # 5. Path exists & reachability
    assert query_engine.path_exists("MD-001", "MC-001")
    assert not query_engine.path_exists("MC-001", "MD-001")

    reachable = query_engine.reachable_entities("MD-001")
    assert len(reachable) == 2
    assert {e.id for e in reachable} == {"MD-001", "MC-001"}


def test_query_engine_missing_entity_raises_error():
    """Verify QueryEntityNotFoundError is raised for non-existent entity IDs."""
    graph = KnowledgeGraph()
    indexer = GraphIndexer(graph=graph)
    traversal = GraphTraversalService(graph=graph, indexer=indexer)
    query_engine = GraphQueryEngine(indexer=indexer, traversal_service=traversal)

    with pytest.raises(QueryEntityNotFoundError):
        query_engine.get_node("MISSING")

    with pytest.raises(QueryEntityNotFoundError):
        query_engine.get_entity("MISSING")

    with pytest.raises(QueryEntityNotFoundError):
        query_engine.get_neighbors("MISSING")

    with pytest.raises(QueryEntityNotFoundError):
        query_engine.path_exists("MISSING", "OTHER")


def test_workspace_graph_query_engine_integration():
    """Integration test running GraphQueryEngine on actual workspace repository graph."""
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

        indexer = GraphIndexer(graph=graph)
        traversal = GraphTraversalService(graph=graph, indexer=indexer)
        query_engine = GraphQueryEngine(indexer=indexer, traversal_service=traversal)

        params = query_engine.get_entities_by_type(EngineeringParameter)
        assert len(params) > 0
        assert isinstance(params[0], EngineeringParameter)
