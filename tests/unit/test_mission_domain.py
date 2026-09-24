"""
Unit tests for MissionDomain domain model.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.mission_domain import MissionDomain


def test_mission_domain_inheritance_and_fields():
    """Verify MissionDomain inherits from KnowledgeEntity and stores category IDs."""
    domain = MissionDomain(
        id="MD-001",
        name="Agriculture",
        description="Agricultural aerial application, crop monitoring, and spraying.",
        category_ids=["MC-001-01", "MC-001-02"]
    )

    assert isinstance(domain, KnowledgeEntity)
    assert isinstance(domain, MissionDomain)
    assert domain.id == "MD-001"
    assert domain.name == "Agriculture"
    assert domain.description == "Agricultural aerial application, crop monitoring, and spraying."
    assert domain.category_ids == ["MC-001-01", "MC-001-02"]


def test_mission_domain_default_category_ids():
    """Verify category_ids defaults to an empty list."""
    domain = MissionDomain(
        id="MD-002",
        name="Cargo Delivery",
        description="Medical, logistics, and last-mile cargo transportation."
    )

    assert domain.category_ids == []


def test_mission_domain_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    domain = MissionDomain(
        id="MD-003",
        name="Surveillance",
        description="Border, perimeter, and tactical surveillance."
    )

    with pytest.raises(AttributeError):
        domain.embedded_object = "Invalid"
