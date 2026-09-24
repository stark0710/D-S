"""
Unit tests for RuleEngine.
"""

import pytest
from backend.rules.models.engineering_rule import EngineeringRule, RuleSeverity
from backend.rules.models.rule_engine_result import RuleEngineResult
from backend.rules.rule_repository import RuleRepository, RuleNotFoundError
from backend.rules.rule_evaluator import RuleEvaluator, MissingRuleContextError
from backend.rules.rule_engine import RuleEngine


@pytest.fixture
def test_rules() -> list[EngineeringRule]:
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
            description="Voltage check",
            category="Electrical",
            severity=RuleSeverity.ERROR,
            condition="battery.voltage == motor.nominal_voltage",
            message="Voltage mismatch."
        ),
        EngineeringRule(
            id="RULE-AERO-001",
            name="Stall Margin",
            description="Stall margin check",
            category="Aerodynamics",
            severity=RuleSeverity.WARNING,
            condition="stall_speed < min_speed",
            message="Insufficient stall margin."
        ),
    ]


def test_evaluate_all_passing(test_rules: list[EngineeringRule]):
    """Verify evaluate_all when all rules pass."""
    repo = RuleRepository(test_rules)
    evaluator = RuleEvaluator()
    engine = RuleEngine(repository=repo, evaluator=evaluator)

    context = {
        "motor": {"current": 40.0, "nominal_voltage": 22.2},
        "esc": {"max_current": 50.0},
        "battery": {"voltage": 22.2},
        "stall_speed": 10.0,
        "min_speed": 15.0
    }

    result = engine.evaluate_all(context)

    assert isinstance(result, RuleEngineResult)
    assert result.overall_passed
    assert result.passed_count == 3
    assert result.failed_count == 0
    assert result.warning_count == 0
    assert result.error_count == 0
    assert result.critical_count == 0
    assert len(result.results) == 3


def test_evaluate_all_with_violations(test_rules: list[EngineeringRule]):
    """Verify evaluate_all statistics aggregation when rules fail across severities."""
    repo = RuleRepository(test_rules)
    evaluator = RuleEvaluator()
    engine = RuleEngine(repository=repo, evaluator=evaluator)

    context = {
        "motor": {"current": 60.0, "nominal_voltage": 22.2},  # Fails R1 (CRITICAL)
        "esc": {"max_current": 50.0},
        "battery": {"voltage": 14.8},  # Fails R2 (ERROR)
        "stall_speed": 20.0,  # Fails R3 (WARNING)
        "min_speed": 15.0
    }

    result = engine.evaluate_all(context)

    assert not result.overall_passed
    assert result.passed_count == 0
    assert result.failed_count == 3
    assert result.critical_count == 1
    assert result.error_count == 1
    assert result.warning_count == 1


def test_evaluate_category(test_rules: list[EngineeringRule]):
    """Verify evaluate_category filters and evaluates rules for the specified category."""
    repo = RuleRepository(test_rules)
    evaluator = RuleEvaluator()
    engine = RuleEngine(repository=repo, evaluator=evaluator)

    context = {
        "motor": {"current": 40.0, "nominal_voltage": 22.2},
        "esc": {"max_current": 50.0},
        "battery": {"voltage": 22.2}
    }

    result = engine.evaluate_category("Electrical", context)

    assert result.overall_passed
    assert len(result.results) == 2
    assert {r.rule_id for r in result.results} == {"RULE-ELEC-001", "RULE-ELEC-002"}


def test_evaluate_rules_by_ids(test_rules: list[EngineeringRule]):
    """Verify evaluate_rules evaluates specific rule IDs."""
    repo = RuleRepository(test_rules)
    evaluator = RuleEvaluator()
    engine = RuleEngine(repository=repo, evaluator=evaluator)

    context = {
        "stall_speed": 10.0,
        "min_speed": 15.0
    }

    result = engine.evaluate_rules(["RULE-AERO-001"], context)

    assert result.overall_passed
    assert len(result.results) == 1
    assert result.results[0].rule_id == "RULE-AERO-001"


def test_evaluate_missing_rule_id_raises_exception(test_rules: list[EngineeringRule]):
    """Verify RuleNotFoundError is propagated when specifying an unknown rule ID."""
    repo = RuleRepository(test_rules)
    evaluator = RuleEvaluator()
    engine = RuleEngine(repository=repo, evaluator=evaluator)

    context = {}

    with pytest.raises(RuleNotFoundError):
        engine.evaluate_rules(["RULE-NONEXISTENT"], context)


def test_evaluator_exception_propagates(test_rules: list[EngineeringRule]):
    """Verify evaluator exceptions (e.g. MissingRuleContextError) propagate cleanly."""
    repo = RuleRepository(test_rules)
    evaluator = RuleEvaluator()
    engine = RuleEngine(repository=repo, evaluator=evaluator)

    context = {}  # Empty context cause MissingRuleContextError

    with pytest.raises(MissingRuleContextError):
        engine.evaluate_all(context)
