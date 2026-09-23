"""
Unit tests for Universal Engineering Constraint Framework.
"""

import pytest
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import ContextBuilder
from backend.design.components.constraints import (
    ConstraintStatus,
    ConstraintSeverity,
    ConstraintIssue,
    ConstraintResult,
    PayloadConstraintRule,
    BudgetConstraintRule,
    FlightTimeConstraintRule,
    ThrustToWeightConstraintRule,
    ConstraintRegistry,
    ConstraintPipeline,
    ConstraintEngine,
)


def test_constraint_enums():
    """Verify ConstraintStatus and ConstraintSeverity enum values."""
    assert ConstraintStatus.SATISFIED == "SATISFIED"
    assert ConstraintStatus.SATISFIED_WITH_WARNINGS == "SATISFIED_WITH_WARNINGS"
    assert ConstraintStatus.VIOLATED == "VIOLATED"
    assert ConstraintSeverity.INFO == "INFO"
    assert ConstraintSeverity.WARNING == "WARNING"
    assert ConstraintSeverity.CRITICAL == "CRITICAL"


def test_payload_constraint_rule():
    """Verify PayloadConstraintRule evaluates payload capacity vs required payload."""
    rule = PayloadConstraintRule()

    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=2.5,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=50.0
    )
    context = ContextBuilder.create_context(req)

    # Satisfied case
    data_ok = {"payload_capacity_kg": 3.0}
    issues_ok = rule.evaluate(data_ok, context)
    assert len(issues_ok) == 0

    # Violated case
    data_bad = {"payload_capacity_kg": 1.5}
    issues_bad = rule.evaluate(data_bad, context)
    assert len(issues_bad) == 1
    assert issues_bad[0].severity == ConstraintSeverity.CRITICAL


def test_budget_constraint_rule():
    """Verify BudgetConstraintRule checks estimated cost vs budget limit."""
    rule = BudgetConstraintRule()

    data_violating = {"estimated_cost": 5000, "budget_limit": 3000}
    issues_critical = rule.evaluate(data_violating)
    assert len(issues_critical) == 1
    assert issues_critical[0].severity == ConstraintSeverity.CRITICAL

    data_warning = {"estimated_cost": 2800, "budget_limit": 3000}
    issues_warn = rule.evaluate(data_warning)
    assert len(issues_warn) == 1
    assert issues_warn[0].severity == ConstraintSeverity.WARNING


def test_constraint_engine_execution():
    """Verify ConstraintEngine evaluates context and design data, identifying satisfied vs violated constraints."""
    engine = ConstraintEngine()

    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=40.0,
        target_range_km=25.0,
        cruise_speed_kmh=60.0,
        budget=4000.0,
        maximum_takeoff_weight_kg=10.0
    )
    context = ContextBuilder.create_context(req)

    # Fully satisfied design
    good_design = {
        "payload_capacity_kg": 2.5,
        "mtow_kg": 7.5,
        "estimated_cost": 3200,
        "endurance_min": 45,
        "range_km": 30,
        "thrust_to_weight_ratio": 2.2
    }

    res_ok = engine.evaluate_constraints(context, good_design)
    assert res_ok.status == ConstraintStatus.SATISFIED
    assert res_ok.overall_score == 1.0
    assert len(res_ok.violated_constraints) == 0

    # Multiple simultaneous violations
    bad_design = {
        "payload_capacity_kg": 1.0,  # Violated (need 2.0)
        "mtow_kg": 12.0,            # Violated (limit 10.0)
        "estimated_cost": 5000,     # Violated (budget 4000)
        "endurance_min": 25,        # Violated (need 40)
        "range_km": 15,             # Violated (need 25)
        "thrust_to_weight_ratio": 1.2  # Violated (< 1.5)
    }

    res_bad = engine.evaluate_constraints(context, bad_design)
    assert res_bad.status == ConstraintStatus.VIOLATED
    assert res_bad.overall_score == 0.0
    assert len(res_bad.violated_constraints) >= 5
