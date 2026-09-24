"""
Unit tests for RelationshipResolver.
"""

from dataclasses import dataclass, field
import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.knowledge_relationship import KnowledgeRelationship
from backend.models.mission_domain import MissionDomain
from backend.models.mission_category import MissionCategory
from backend.models.engineering_parameter import EngineeringParameter
from backend.knowledge.graph.knowledge_graph import KnowledgeGraph
from backend.knowledge.graph.relationship_resolver import (
    RelationshipResolver,
    UnresolvedRelationshipError,
)


@dataclass(slots=True)
class EntityWithRelationships(KnowledgeEntity):
    relationships: list[KnowledgeRelationship] = field(default_factory=list)


def test_relationship_resolver_success():
    """Verify RelationshipResolver converts KnowledgeRelationship objects to GraphEdges and updates node adjacency."""
    rel = KnowledgeRelationship(
        source_id="E-001",
        source_type="Entity",
        target_id="E-002",
        target_type="Entity",
        relationship_type="depends_on"
    )

    e1 = EntityWithRelationships(id="E-001", name="Entity 1", description="Desc 1", relationships=[rel])
    e2 = KnowledgeEntity(id="E-002", name="Entity 2", description="Desc 2")

    graph = KnowledgeGraph()
    graph.add_entity(e1)
    graph.add_entity(e2)

    resolver = RelationshipResolver(graph=graph)
    resolver.resolve()

    assert graph.relationship_count() == 1

    node1 = graph.get_node("E-001")
    node2 = graph.get_node("E-002")

    assert len(node1.outgoing_edges) == 1
    assert len(node1.incoming_edges) == 0
    assert node1.outgoing_edges[0].target_id == "E-002"
    assert node1.outgoing_edges[0].relationship_type == "depends_on"

    assert len(node2.incoming_edges) == 1
    assert len(node2.outgoing_edges) == 0
    assert node2.incoming_edges[0].source_id == "E-001"


def test_unresolved_target_raises_exception():
    """Verify UnresolvedRelationshipError is raised if target entity is absent from graph."""
    rel = KnowledgeRelationship(
        source_id="E-001",
        source_type="Entity",
        target_id="MISSING-TARGET",
        target_type="Entity",
        relationship_type="requires"
    )

    e1 = EntityWithRelationships(id="E-001", name="Entity 1", description="Desc 1", relationships=[rel])

    graph = KnowledgeGraph()
    graph.add_entity(e1)

    resolver = RelationshipResolver(graph=graph)

    with pytest.raises(UnresolvedRelationshipError):
        resolver.resolve()


def test_mission_domain_implicit_category_resolution():
    """Verify implicit category_ids on MissionDomain are resolved into contains relationships."""
    md = MissionDomain(id="MD-001", name="Agriculture", description="Ag", category_ids=["MC-001"])
    mc = MissionCategory(
        id="MC-001",
        name="Crop Spraying",
        description="Spraying",
        domain_id="MD-001",
        objective="Crop Protection",
        engineering_parameter_ids=[]
    )

    graph = KnowledgeGraph()
    graph.add_entity(md)
    graph.add_entity(mc)

    resolver = RelationshipResolver(graph=graph)
    resolver.resolve()

    assert graph.relationship_count() == 1

    node_md = graph.get_node("MD-001")
    node_mc = graph.get_node("MC-001")

    assert len(node_md.outgoing_edges) == 1
    assert node_md.outgoing_edges[0].relationship_type == "contains"
    assert node_md.outgoing_edges[0].target_id == "MC-001"

    assert len(node_mc.incoming_edges) == 1
    assert node_mc.incoming_edges[0].source_id == "MD-001"
