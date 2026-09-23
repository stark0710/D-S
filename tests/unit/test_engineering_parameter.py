"""
Unit tests for EngineeringParameter domain model.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.models.engineering_parameter import EngineeringParameter


def test_engineering_parameter_inheritance():
    """Verify EngineeringParameter inherits from KnowledgeEntity."""
    param = EngineeringParameter(
        id="MP-001-001",
        name="Payload Weight",
        description="Weight of cargo or mission equipment.",
        library="EPL-001_MISSION_PROFILE",
        parameter_group="Mission Requirements",
        engineering_classification="Operational",
        unit="kg",
        data_type="Float",
        default_value="5.0",
        allowed_values=[],
        reference_ids=["REF-STANAG-4703"]
    )

    assert isinstance(param, KnowledgeEntity)
    assert isinstance(param, EngineeringParameter)
    assert param.id == "MP-001-001"
    assert param.name == "Payload Weight"
    assert param.description == "Weight of cargo or mission equipment."
    assert param.library == "EPL-001_MISSION_PROFILE"
    assert param.parameter_group == "Mission Requirements"
    assert param.engineering_classification == "Operational"
    assert param.unit == "kg"
    assert param.data_type == "Float"
    assert param.default_value == "5.0"
    assert param.reference_ids == ["REF-STANAG-4703"]


def test_engineering_parameter_defaults():
    """Verify default values for optional fields and list factories."""
    param = EngineeringParameter(
        id="MP-001-002",
        name="Cruise Speed",
        description="Target cruise speed of UAV.",
        library="EPL-001_MISSION_PROFILE",
        parameter_group="Performance Requirements",
        engineering_classification="Performance"
    )

    assert param.unit is None
    assert param.data_type is None
    assert param.default_value is None
    assert param.allowed_values == []
    assert param.reference_ids == []


def test_engineering_parameter_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    param = EngineeringParameter(
        id="MP-001-003",
        name="Flight Time",
        description="Required endurance.",
        library="EPL-001_MISSION_PROFILE",
        parameter_group="Mission Requirements",
        engineering_classification="Operational"
    )

    with pytest.raises(AttributeError):
        param.arbitrary_field = "Invalid"
