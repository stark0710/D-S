"""
Unit tests for KnowledgeReference domain model.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.knowledge_reference import KnowledgeReference


def test_knowledge_reference_instantiation():
    """Verify KnowledgeReference initializes correctly with required fields."""
    ref = KnowledgeReference(
        entity_id="MP-001-001",
        entity_type="EngineeringParameter",
        source_document="docs/engineering_knowledge_base/mission_parameters/MP-001-001.md",
        reference_type="SourceDocument"
    )

    assert ref.entity_id == "MP-001-001"
    assert ref.entity_type == "EngineeringParameter"
    assert ref.source_document == "docs/engineering_knowledge_base/mission_parameters/MP-001-001.md"
    assert ref.reference_type == "SourceDocument"


def test_knowledge_reference_does_not_inherit_knowledge_entity():
    """Verify KnowledgeReference does NOT inherit from KnowledgeEntity."""
    ref = KnowledgeReference(
        entity_id="MC-001-01",
        entity_type="MissionCategory",
        source_document="STANAG 4703 UAV Airworthiness Standard",
        reference_type="Standard"
    )

    assert not isinstance(ref, KnowledgeEntity)


def test_knowledge_reference_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    ref = KnowledgeReference(
        entity_id="MD-001",
        entity_type="MissionDomain",
        source_document="Agriculture Spec",
        reference_type="Specification"
    )

    with pytest.raises(AttributeError):
        ref.extra_attribute = "Invalid"
