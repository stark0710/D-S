"""
Unit tests for RuleEvaluator.
"""

import pytest
from backend.rules.models.engineering_rule import EngineeringRule, RuleSeverity
from backend.rules.models.rule_evaluation_result import RuleEvaluationResult
from backend.rules.rule_evaluator import (
    RuleEvaluator,
    InvalidRuleExpressionError,
    MissingRuleContextError,
)


def test_rule_evaluator_operators_passing():
    """Verify RuleEvaluator evaluates all comparison operators correctly when conditions pass."""
    evaluator = RuleEvaluator()

    context = {
        "motor.current": 40.0,
        "esc.max_current": 50.0,
        "battery.voltage": 22.2,
        "motor.nominal_voltage": 22.2,
        "payload.weight": 2.5,
        "aircraft.max_payload": 5.0,
        "thrust.total": 12.0,
        "aircraft.required_thrust": 6.0,
        "status": "FROZEN"
    }

    # 1. <= (Less than or equal)
    r1 = EngineeringRule(
        id="R1", name="N1", description="D", category="Electrical",
        severity=RuleSeverity.CRITICAL, condition="motor.current <= esc.max_current", message="Failed"
    )
    res1 = evaluator.evaluate(r1, context)
    assert res1.passed
    assert res1.message == ""
    assert res1.evaluation_time_ms >= 0.0

    # 2. == (Equal)
    r2 = EngineeringRule(
        id="R2", name="N2", description="D", category="Electrical",
        severity=RuleSeverity.ERROR, condition="battery.voltage == motor.nominal_voltage", message="Failed"
    )
    res2 = evaluator.evaluate(r2, context)
    assert res2.passed

    # 3. >= (Greater than or equal)
    r3 = EngineeringRule(
        id="R3", name="N3", description="D", category="Propulsion",
        severity=RuleSeverity.WARNING, condition="thrust.total >= aircraft.required_thrust", message="Failed"
    )
    res3 = evaluator.evaluate(r3, context)
    assert res3.passed

    # 4. String equality
    r4 = EngineeringRule(
        id="R4", name="N4", description="D", category="Status",
        severity=RuleSeverity.INFO, condition='status == "FROZEN"', message="Failed"
    )
    res4 = evaluator.evaluate(r4, context)
    assert res4.passed


def test_rule_evaluator_failing_condition():
    """Verify failing rule condition populates failure message and details."""
    evaluator = RuleEvaluator()

    context = {
        "motor": {"current": 60.0},
        "esc": {"max_current": 50.0}
    }

    rule = EngineeringRule(
        id="R-FAIL",
        name="ESC Overcurrent",
        description="Overcurrent test",
        category="Electrical",
        severity=RuleSeverity.CRITICAL,
        condition="motor.current <= esc.max_current",
        message="Motor peak current exceeds ESC continuous rating."
    )

    res = evaluator.evaluate(rule, context)

    assert not res.passed
    assert res.rule_id == "R-FAIL"
    assert res.severity == RuleSeverity.CRITICAL
    assert res.message == "Motor peak current exceeds ESC continuous rating."
    assert res.details["lhs_val"] == 60.0
    assert res.details["rhs_val"] == 50.0


def test_numeric_literal_comparison():
    """Verify comparing variable to numeric literal."""
    evaluator = RuleEvaluator()
    context = {"thrust_weight_ratio": 2.5}

    rule = EngineeringRule(
        id="R-LITERAL",
        name="TWR Check",
        description="Desc",
        category="Performance",
        severity=RuleSeverity.WARNING,
        condition="thrust_weight_ratio >= 2.0",
        message="Insufficient TWR"
    )

    res = evaluator.evaluate(rule, context)
    assert res.passed


def test_missing_context_variable_raises_exception():
    """Verify MissingRuleContextError is raised when referenced context variable is absent."""
    evaluator = RuleEvaluator()
    context = {"motor.current": 40.0}  # Missing esc.max_current

    rule = EngineeringRule(
        id="R-MISSING",
        name="Test",
        description="Desc",
        category="Test",
        severity=RuleSeverity.ERROR,
        condition="motor.current <= esc.max_current",
        message="Failed"
    )

    with pytest.raises(MissingRuleContextError):
        evaluator.evaluate(rule, context)


def test_invalid_expression_raises_exception():
    """Verify InvalidRuleExpressionError is raised for malformed conditions."""
    evaluator = RuleEvaluator()
    context = {"a": 10}

    # Missing operator
    r1 = EngineeringRule(
        id="R-INVALID1", name="T", description="D", category="C",
        severity=RuleSeverity.INFO, condition="motor.current 50", message="M"
    )
    with pytest.raises(InvalidRuleExpressionError):
        evaluator.evaluate(r1, context)

    # Empty condition
    r2 = EngineeringRule(
        id="R-INVALID2", name="T", description="D", category="C",
        severity=RuleSeverity.INFO, condition="", message="M"
    )
    with pytest.raises(InvalidRuleExpressionError):
        evaluator.evaluate(r2, context)
