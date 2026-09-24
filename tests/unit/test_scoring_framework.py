"""
Unit tests for Universal Engineering Scoring Framework.
"""

import pytest
from backend.design.common.requirements import (
    MissionType,
    OptimizationPriority,
    RequirementModel,
)
from backend.design.common.context import ContextBuilder
from backend.design.components.scoring import (
    ScoreCategory,
    ScoreWeight,
    ScoreBreakdown,
    EngineeringScore,
    PayloadScoreRule,
    EnduranceScoreRule,
    CostScoreRule,
    ScoringRegistry,
    ScoringPipeline,
    ScoringEngine,
)


def test_scoring_enums():
    """Verify ScoreCategory enum values."""
    assert ScoreCategory.PAYLOAD == "PAYLOAD"
    assert ScoreCategory.ENDURANCE == "ENDURANCE"
    assert ScoreCategory.RANGE == "RANGE"
    assert ScoreCategory.COST == "COST"
    assert ScoreCategory.SAFETY == "SAFETY"


def test_payload_and_endurance_rules():
    """Verify PayloadScoreRule and EnduranceScoreRule evaluation."""
    payload_rule = PayloadScoreRule()
    endurance_rule = EnduranceScoreRule()

    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=3.0,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=60.0
    )
    context = ContextBuilder.create_context(req)

    # Fully meeting requirements -> score 1.0
    design_ok = {"payload_capacity_kg": 3.0, "endurance_min": 45.0}
    p_score, _ = payload_rule.evaluate(design_ok, context)
    e_score, _ = endurance_rule.evaluate(design_ok, context)
    assert p_score == 1.0
    assert e_score == 1.0

    # Partial meeting -> ratio score
    design_partial = {"payload_capacity_kg": 1.5, "endurance_min": 22.5}
    p_score_p, _ = payload_rule.evaluate(design_partial, context)
    e_score_p, _ = endurance_rule.evaluate(design_partial, context)
    assert p_score_p == 0.50
    assert e_score_p == 0.50


def test_priority_weighting():
    """Verify ScoringPipeline alters overall score based on OptimizationPriority."""
    req_cost = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=50.0,
        budget=5000.0,
        optimization_priority=OptimizationPriority.LOWEST_COST
    )
    context = ContextBuilder.create_context(req_cost)

    # Design with great cost savings ($1000 cost vs $5000 budget) but poor payload (0.5 kg vs 1.0 kg)
    cheap_design = {
        "payload_capacity_kg": 0.5,
        "endurance_min": 20.0,
        "range_km": 10.0,
        "estimated_cost": 1000.0,
        "mtow_kg": 2.0,
        "thrust_to_weight_ratio": 2.0
    }

    engine = ScoringEngine()
    score_cost_prio = engine.score_design(context, cheap_design)

    # Should have higher overall score under LOWEST_COST priority than under MAXIMUM_PAYLOAD priority
    req_payload = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=20.0,
        target_range_km=10.0,
        cruise_speed_kmh=50.0,
        budget=5000.0,
        optimization_priority=OptimizationPriority.MAXIMUM_PAYLOAD
    )
    context_payload = ContextBuilder.create_context(req_payload)
    score_payload_prio = engine.score_design(context_payload, cheap_design)

    assert score_cost_prio.overall_score > score_payload_prio.overall_score


def test_scoring_engine_execution():
    """Verify ScoringEngine generates EngineeringScore with breakdowns, strengths, and weaknesses."""
    engine = ScoringEngine()

    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=5.0,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=70.0,
        budget=6000.0
    )
    context = ContextBuilder.create_context(req)

    design = {
        "payload_capacity_kg": 5.0,
        "endurance_min": 35.0,
        "range_km": 30.0,
        "estimated_cost": 4000.0,
        "mtow_kg": 8.0,
        "thrust_to_weight_ratio": 2.2
    }

    score_result = engine.score_design(context, design)

    assert isinstance(score_result, EngineeringScore)
    assert score_result.overall_score >= 0.85
    assert len(score_result.score_breakdown) >= 5
    assert len(score_result.strengths) >= 3
