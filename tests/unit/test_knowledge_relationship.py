"""
Unit tests for KnowledgeRelationship domain model.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.knowledge_relationship import KnowledgeRelationship


def test_knowledge_relationship_instantiation():
    """Verify KnowledgeRelationship initializes correctly with required fields."""
    rel = KnowledgeRelationship(
        source_id="MD-001",
        source_type="MissionDomain",
        target_id="MC-001-01",
        target_type="MissionCategory",
        relationship_type="CONTAINS"
    )

    assert rel.source_id == "MD-001"
    assert rel.source_type == "MissionDomain"
    assert rel.target_id == "MC-001-01"
    assert rel.target_type == "MissionCategory"
    assert rel.relationship_type == "CONTAINS"


def test_knowledge_relationship_does_not_inherit_knowledge_entity():
    """Verify KnowledgeRelationship does NOT inherit from KnowledgeEntity."""
    rel = KnowledgeRelationship(
        source_id="MC-001-01",
        source_type="MissionCategory",
        target_id="MP-001-001",
        target_type="EngineeringParameter",
        relationship_type="REQUIRES"
    )

    assert not isinstance(rel, KnowledgeEntity)


def test_knowledge_relationship_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    rel = KnowledgeRelationship(
        source_id="MP-001-001",
        source_type="EngineeringParameter",
        target_id="MP-001-002",
        target_type="EngineeringParameter",
        relationship_type="DEPENDS_ON"
    )

    with pytest.raises(AttributeError):
        rel.object_reference = "Invalid"
