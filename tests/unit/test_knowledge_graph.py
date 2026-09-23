"""
Unit tests for KnowledgeGraph.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.engineering_parameter import EngineeringParameter
from backend.models.mission_domain import MissionDomain
from backend.models.knowledge_relationship import KnowledgeRelationship
from backend.knowledge.graph.knowledge_graph import (
    KnowledgeGraph,
    DuplicateGraphEntityError,
    InvalidRelationshipError,
    GraphEntityNotFoundError,
)


def test_knowledge_graph_entity_management():
    """Verify adding, getting, checking presence, and counting graph entity nodes."""
    graph = KnowledgeGraph()

    e1 = EngineeringParameter(
        id="EP-001",
        name="Wing Span",
        description="Wing span",
        library="EPL-001",
        parameter_group="Geometry",
        engineering_classification="Physical"
    )

    e2 = MissionDomain(
        id="MD-001",
        name="Agriculture",
        description="Ag domain",
        category_ids=[]
    )

    assert graph.entity_count() == 0
    assert graph.entities() == []

    graph.add_entity(e1)
    graph.add_entity(e2)

    assert graph.entity_count() == 2
    assert graph.has_entity("EP-001")
    assert graph.has_entity("MD-001")
    assert not graph.has_entity("EP-999")

    assert graph.get_entity("EP-001") == e1
    assert graph.get_entity("MD-001") == e2


def test_duplicate_entity_rejection():
    """Verify DuplicateGraphEntityError is raised when adding duplicate entity ID."""
    graph = KnowledgeGraph()
    e1 = KnowledgeEntity(id="EP-001", name="Param 1", description="Desc 1")
    e2 = KnowledgeEntity(id="EP-001", name="Param 2", description="Desc 2")

    graph.add_entity(e1)

    with pytest.raises(DuplicateGraphEntityError):
        graph.add_entity(e2)


def test_missing_entity_lookup_raises_error():
    """Verify GraphEntityNotFoundError is raised when querying missing entity ID."""
    graph = KnowledgeGraph()

    with pytest.raises(GraphEntityNotFoundError):
        graph.get_entity("MISSING-ID")


def test_relationship_management_and_referential_integrity():
    """Verify adding relationships, adjacency list indexing, and node presence validation."""
    graph = KnowledgeGraph()

    e1 = KnowledgeEntity(id="MD-001", name="Agriculture", description="Domain")
    e2 = KnowledgeEntity(id="MC-001-01", name="Crop Spraying", description="Category")

    graph.add_entity(e1)
    graph.add_entity(e2)

    rel = KnowledgeRelationship(
        source_id="MD-001",
        source_type="MissionDomain",
        target_id="MC-001-01",
        target_type="MissionCategory",
        relationship_type="CONTAINS"
    )

    assert graph.relationship_count() == 0
    graph.add_relationship(rel)

    assert graph.relationship_count() == 1
    assert graph.relationships() == [rel]

    # Test adjacency lookup
    outgoing = graph.get_relationships("MD-001")
    assert len(outgoing) == 1
    assert outgoing[0] == rel

    # Target node has no outgoing relationships
    assert graph.get_relationships("MC-001-01") == []


def test_invalid_relationship_missing_source():
    """Verify InvalidRelationshipError is raised if source entity ID is missing."""
    graph = KnowledgeGraph()
    target = KnowledgeEntity(id="TARGET-001", name="Target", description="Desc")
    graph.add_entity(target)

    rel = KnowledgeRelationship(
        source_id="MISSING-SOURCE",
        source_type="Unknown",
        target_id="TARGET-001",
        target_type="Entity",
        relationship_type="LINKS"
    )

    with pytest.raises(InvalidRelationshipError):
        graph.add_relationship(rel)


def test_invalid_relationship_missing_target():
    """Verify InvalidRelationshipError is raised if target entity ID is missing."""
    graph = KnowledgeGraph()
    source = KnowledgeEntity(id="SOURCE-001", name="Source", description="Desc")
    graph.add_entity(source)

    rel = KnowledgeRelationship(
        source_id="SOURCE-001",
        source_type="Entity",
        target_id="MISSING-TARGET",
        target_type="Unknown",
        relationship_type="LINKS"
    )

    with pytest.raises(InvalidRelationshipError):
        graph.add_relationship(rel)
