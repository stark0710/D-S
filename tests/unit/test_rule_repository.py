"""
Unit tests for RuleRepository.
"""

import pytest
from backend.rules.models.engineering_rule import EngineeringRule, RuleSeverity
from backend.rules.rule_repository import (
    RuleRepository,
    DuplicateRuleIDError,
    RuleNotFoundError,
)


@pytest.fixture
def sample_rules() -> list[EngineeringRule]:
    return [
        EngineeringRule(
            id="RULE-ELEC-001",
            name="ESC Current Limit",
            description="ESC rating check",
            category="Electrical",
            severity=RuleSeverity.CRITICAL,
            condition="motor.current <= esc.max_current",
            message="Motor current exceeds ESC rating."
        ),
        EngineeringRule(
            id="RULE-ELEC-002",
            name="Voltage Match",
            description="Nominal voltage match",
            category="Electrical",
            severity=RuleSeverity.ERROR,
            condition="battery.voltage == motor.nominal_voltage",
            message="Voltage mismatch."
        ),
        EngineeringRule(
            id="RULE-AERO-001",
            name="Stall Margin",
            description="Stall speed safety margin",
            category="Aerodynamics",
            severity=RuleSeverity.WARNING,
            condition="stall_speed < min_speed",
            message="Insufficient stall margin."
        ),
    ]


def test_rule_repository_lookups(sample_rules: list[EngineeringRule]):
    """Verify get_all, get_rule, has_rule, get_by_category, get_by_severity, count, and categories."""
    repo = RuleRepository(sample_rules)

    assert repo.count() == 3
    assert len(repo.get_all()) == 3

    # ID lookup
    assert repo.has_rule("RULE-ELEC-001")
    assert not repo.has_rule("RULE-NONEXISTENT")

    rule1 = repo.get_rule("RULE-ELEC-001")
    assert rule1.name == "ESC Current Limit"

    # Category lookup
    elec_rules = repo.get_by_category("Electrical")
    assert len(elec_rules) == 2
    assert {r.id for r in elec_rules} == {"RULE-ELEC-001", "RULE-ELEC-002"}

    aero_rules = repo.get_by_category("aerodynamics")  # Case insensitive
    assert len(aero_rules) == 1
    assert aero_rules[0].id == "RULE-AERO-001"

    # Severity lookup
    crit_rules = repo.get_by_severity(RuleSeverity.CRITICAL)
    assert len(crit_rules) == 1
    assert crit_rules[0].id == "RULE-ELEC-001"

    warn_rules = repo.get_by_severity("WARNING")  # String representation
    assert len(warn_rules) == 1
    assert warn_rules[0].id == "RULE-AERO-001"

    # Categories list
    assert repo.categories() == ["Aerodynamics", "Electrical"]


def test_rule_not_found_raises_exception(sample_rules: list[EngineeringRule]):
    """Verify RuleNotFoundError is raised when querying a non-existent rule ID."""
    repo = RuleRepository(sample_rules)

    with pytest.raises(RuleNotFoundError):
        repo.get_rule("RULE-999")


def test_duplicate_rule_id_raises_exception():
    """Verify DuplicateRuleIDError is raised during initialization if rule IDs collide."""
    r1 = EngineeringRule(
        id="DUP-001", name="Rule 1", description="D", category="Cat",
        severity=RuleSeverity.INFO, condition="c1", message="m1"
    )
    r2 = EngineeringRule(
        id="DUP-001", name="Rule 2", description="D", category="Cat",
        severity=RuleSeverity.INFO, condition="c2", message="m2"
    )

    with pytest.raises(DuplicateRuleIDError):
        RuleRepository([r1, r2])


def test_empty_rule_repository():
    """Verify behavior of empty RuleRepository."""
    repo = RuleRepository()

    assert repo.count() == 0
    assert repo.get_all() == []
    assert repo.categories() == []
    assert repo.get_by_category("Electrical") == []
    assert repo.get_by_severity(RuleSeverity.CRITICAL) == []
    assert not repo.has_rule("RULE-001")
