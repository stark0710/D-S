"""
Unit tests for GraphTraversalService.
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
from backend.knowledge.graph.graph_builder import GraphBuilder
from backend.knowledge.graph.relationship_resolver import RelationshipResolver
from backend.knowledge.graph.graph_construction_pipeline import GraphConstructionPipeline
from backend.knowledge.graph.graph_indexer import GraphIndexer
from backend.knowledge.graph.graph_traversal_service import (
    GraphTraversalService,
    TraversalNodeNotFoundError,
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


def test_bfs_dfs_and_path_exists():
    """Verify BFS, DFS, reachability, neighbors, and path existence detection."""
    # Build graph: A -> B -> C, and isolated D
    nA = KnowledgeEntity(id="A", name="Node A", description="Desc A")
    nB = KnowledgeEntity(id="B", name="Node B", description="Desc B")
    nC = KnowledgeEntity(id="C", name="Node C", description="Desc C")
    nD = KnowledgeEntity(id="D", name="Node D", description="Desc D")

    graph = KnowledgeGraph()
    for n in [nA, nB, nC, nD]:
        graph.add_entity(n)

    edge1 = GraphEdge(source_id="A", target_id="B", relationship_type="depends_on")
    edge2 = GraphEdge(source_id="B", target_id="C", relationship_type="depends_on")

    graph.add_relationship(edge1)
    graph.add_relationship(edge2)

    indexer = GraphIndexer(graph=graph)
    traversal = GraphTraversalService(graph=graph, indexer=indexer)

    # 1. BFS
    bfs_nodes = traversal.breadth_first_search("A")
    assert [n.id() for n in bfs_nodes] == ["A", "B", "C"]

    # 2. DFS
    dfs_nodes = traversal.depth_first_search("A")
    assert [n.id() for n in dfs_nodes] == ["A", "B", "C"]

    # 3. Neighbors
    neighbors_B = traversal.neighbors("B")
    assert {n.id() for n in neighbors_B} == {"A", "C"}

    # 4. Reachable nodes
    reachable = traversal.reachable_nodes("A")
    assert {n.id() for n in reachable} == {"A", "B", "C"}

    # 5. Path exists
    assert traversal.path_exists("A", "C")
    assert traversal.path_exists("A", "B")
    assert traversal.path_exists("A", "A")
    assert not traversal.path_exists("A", "D")
    assert not traversal.path_exists("C", "A")  # Directed graph edge


def test_missing_node_raises_traversal_error():
    """Verify TraversalNodeNotFoundError is raised when querying missing entity IDs."""
    graph = KnowledgeGraph()
    indexer = GraphIndexer(graph=graph)
    traversal = GraphTraversalService(graph=graph, indexer=indexer)

    with pytest.raises(TraversalNodeNotFoundError):
        traversal.breadth_first_search("MISSING")

    with pytest.raises(TraversalNodeNotFoundError):
        traversal.depth_first_search("MISSING")

    with pytest.raises(TraversalNodeNotFoundError):
        traversal.neighbors("MISSING")

    with pytest.raises(TraversalNodeNotFoundError):
        traversal.path_exists("MISSING", "OTHER")


def test_workspace_graph_traversal_integration():
    """Integration test executing GraphTraversalService on workspace repository graph."""
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

        nodes = graph.nodes()
        if nodes:
            start_id = nodes[0].id()
            bfs_result = traversal.breadth_first_search(start_id)
            assert len(bfs_result) >= 1
            assert bfs_result[0].id() == start_id
