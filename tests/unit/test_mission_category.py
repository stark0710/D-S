"""
Unit tests for MissionCategory domain model.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.mission_category import MissionCategory


def test_mission_category_inheritance_and_fields():
    """Verify MissionCategory inherits from KnowledgeEntity and stores required domain fields."""
    category = MissionCategory(
        id="MC-001-01",
        name="Crop Spraying",
        description="Aerial dispersion of liquid fertilizers and pesticides.",
        domain_id="MD-001",
        objective="Deliver liquid chemicals uniformly over crop fields.",
        engineering_parameter_ids=["MP-001-001", "MP-001-002", "MP-006-002"]
    )

    assert isinstance(category, KnowledgeEntity)
    assert isinstance(category, MissionCategory)
    assert category.id == "MC-001-01"
    assert category.name == "Crop Spraying"
    assert category.description == "Aerial dispersion of liquid fertilizers and pesticides."
    assert category.domain_id == "MD-001"
    assert category.objective == "Deliver liquid chemicals uniformly over crop fields."
    assert category.engineering_parameter_ids == ["MP-001-001", "MP-001-002", "MP-006-002"]


def test_mission_category_default_parameter_ids():
    """Verify engineering_parameter_ids defaults to an empty list."""
    category = MissionCategory(
        id="MC-002-01",
        name="Parcel Delivery",
        description="Last-mile delivery of commercial cargo.",
        domain_id="MD-002",
        objective="Transport package safely to target coordinates."
    )

    assert category.engineering_parameter_ids == []


def test_mission_category_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    category = MissionCategory(
        id="MC-003-01",
        name="Border Surveillance",
        description="Continuous visual and thermal monitoring of border regions.",
        domain_id="MD-003",
        objective="Provide long-endurance video feeds."
    )

    with pytest.raises(AttributeError):
        category.embedded_param_object = "Invalid"
