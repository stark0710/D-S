"""
Unit tests for EngineeringRule and RuleSeverity domain models.
"""

import pytest
from backend.models.knowledge_entity import KnowledgeEntity
from backend.rules.models.engineering_rule import EngineeringRule, RuleSeverity


def test_rule_severity_enum():
    """Verify RuleSeverity enum values."""
    assert RuleSeverity.INFO == "INFO"
    assert RuleSeverity.WARNING == "WARNING"
    assert RuleSeverity.ERROR == "ERROR"
    assert RuleSeverity.CRITICAL == "CRITICAL"


def test_engineering_rule_instantiation():
    """Verify EngineeringRule initializes correctly and inherits from KnowledgeEntity."""
    rule = EngineeringRule(
        id="RULE-ELEC-001",
        name="ESC Current Limit",
        description="Ensures motor current does not exceed ESC rating",
        category="Electrical",
        severity=RuleSeverity.CRITICAL,
        condition="motor.current <= esc.max_current",
        message="Motor current exceeds continuous rating of ESC.",
        metadata={"subsystem": "Powertrain"}
    )

    assert isinstance(rule, KnowledgeEntity)
    assert rule.id == "RULE-ELEC-001"
    assert rule.name == "ESC Current Limit"
    assert rule.description == "Ensures motor current does not exceed ESC rating"
    assert rule.category == "Electrical"
    assert rule.severity == RuleSeverity.CRITICAL
    assert rule.condition == "motor.current <= esc.max_current"
    assert rule.message == "Motor current exceeds continuous rating of ESC."
    assert rule.metadata == {"subsystem": "Powertrain"}


def test_engineering_rule_defaults():
    """Verify default metadata attribute."""
    rule = EngineeringRule(
        id="RULE-AERO-001",
        name="Stall Speed Safety Margin",
        description="Verifies stall speed margin",
        category="Aerodynamics",
        severity=RuleSeverity.ERROR,
        condition="stall_speed < min_operating_speed",
        message="Stall speed exceeds minimum safe operating speed."
    )

    assert rule.metadata == {}


def test_engineering_rule_slots():
    """Verify slots prevent arbitrary attribute assignment."""
    rule = EngineeringRule(
        id="RULE-001",
        name="Test Rule",
        description="Desc",
        category="Test",
        severity=RuleSeverity.INFO,
        condition="a == b",
        message="Test message"
    )

    with pytest.raises(AttributeError):
        rule.arbitrary_field = "Invalid"
