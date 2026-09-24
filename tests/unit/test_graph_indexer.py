"""
Unit tests for GraphIndexer.
"""

from pathlib import Path
import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.mission_domain import MissionDomain
from backend.models.mission_category import MissionCategory
from backend.models.engineering_parameter import EngineeringParameter
from backend.knowledge.knowledge_repository import KnowledgeRepository
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.graph_builder import GraphBuilder
from backend.knowledge.graph.relationship_resolver import RelationshipResolver
from backend.knowledge.graph.graph_construction_pipeline import GraphConstructionPipeline
from backend.knowledge.graph.graph_indexer import GraphIndexer, GraphNodeNotFoundError
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


def test_graph_indexer_lookups():
    """Verify get_node_by_id, get_nodes_by_label, get_nodes_by_entity_type, get_edges_by_relationship, and get_neighbors."""
    md = MissionDomain(id="MD-001", name="Agriculture", description="Ag", category_ids=["MC-001"])
    mc = MissionCategory(id="MC-001", name="Crop Spraying", description="Spraying", domain_id="MD-001", objective="Crop Protection", engineering_parameter_ids=[])

    graph = KnowledgeGraph()
    graph.add_entity(md)
    graph.add_entity(mc)

    resolver = RelationshipResolver(graph=graph)
    resolver.resolve()

    indexer = GraphIndexer(graph=graph)

    # 1. ID lookup
    node_md = indexer.get_node_by_id("MD-001")
    assert node_md.id() == "MD-001"
    assert node_md.entity == md

    # 2. Label lookup
    md_nodes = indexer.get_nodes_by_label("MissionDomain")
    assert len(md_nodes) == 1
    assert md_nodes[0].id() == "MD-001"

    # 3. Entity type lookup
    mc_nodes = indexer.get_nodes_by_entity_type(MissionCategory)
    assert len(mc_nodes) == 1
    assert mc_nodes[0].id() == "MC-001"

    # 4. Relationship lookup
    contains_edges = indexer.get_edges_by_relationship("contains")
    assert len(contains_edges) == 1
    assert contains_edges[0].source_id == "MD-001"
    assert contains_edges[0].target_id == "MC-001"

    # 5. Neighbor lookup
    neighbors_md = indexer.get_neighbors("MD-001")
    assert len(neighbors_md) == 1
    assert neighbors_md[0].id() == "MC-001"

    neighbors_mc = indexer.get_neighbors("MC-001")
    assert len(neighbors_mc) == 1
    assert neighbors_mc[0].id() == "MD-001"


def test_missing_node_id_raises_error():
    """Verify GraphNodeNotFoundError is raised for non-existent node IDs."""
    graph = KnowledgeGraph()
    indexer = GraphIndexer(graph=graph)

    with pytest.raises(GraphNodeNotFoundError):
        indexer.get_node_by_id("NONEXISTENT-ID")


def test_workspace_graph_indexer_integration():
    """Integration test running GraphIndexer on workspace KnowledgeGraph."""
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

        indexer = GraphIndexer(graph=graph)

        ep_nodes = indexer.get_nodes_by_entity_type(EngineeringParameter)
        assert len(ep_nodes) > 0
