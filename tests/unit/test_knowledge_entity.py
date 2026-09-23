"""
Unit tests for KnowledgeEntity domain model.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity


def test_knowledge_entity_instantiation():
    """Verify KnowledgeEntity initializes correctly with required fields."""
    entity = KnowledgeEntity(
        id="KE-001",
        name="Maximum Takeoff Weight",
        description="The maximum allowable weight of the aircraft at takeoff."
    )

    assert entity.id == "KE-001"
    assert entity.name == "Maximum Takeoff Weight"
    assert entity.description == "The maximum allowable weight of the aircraft at takeoff."


def test_knowledge_entity_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    entity = KnowledgeEntity(
        id="KE-002",
        name="Cruise Speed",
        description="Design level cruise speed."
    )

    with pytest.raises(AttributeError):
        entity.custom_attr = "Invalid attribute assignment"


def test_knowledge_entity_equality():
    """Verify dataclass equality behavior based on field values."""
    entity1 = KnowledgeEntity(id="1", name="Test", description="Desc")
    entity2 = KnowledgeEntity(id="1", name="Test", description="Desc")
    entity3 = KnowledgeEntity(id="2", name="Test", description="Desc")

    assert entity1 == entity2
    assert entity1 != entity3
