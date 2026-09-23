"""
Unit tests for Universal Engineering Optimization Framework.
"""

import pytest
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import DesignStage, DesignStatus, ContextBuilder
from backend.design.components.optimization import (
    OptimizationGoal,
    OptimizationCandidate,
    OptimizationIteration,
    OptimizationResult,
    OptimizationStopCondition,
    GreedyOptimizationStrategy,
    HillClimbingStrategy,
    OptimizationRegistry,
    OptimizationPipeline,
    OptimizationEngine,
)


def test_optimization_enums():
    """Verify OptimizationGoal enum values."""
    assert OptimizationGoal.MINIMUM_WEIGHT == "MINIMUM_WEIGHT"
    assert OptimizationGoal.MINIMUM_COST == "MINIMUM_COST"
    assert OptimizationGoal.MAXIMUM_FLIGHT_TIME == "MAXIMUM_FLIGHT_TIME"
    assert OptimizationGoal.MAXIMUM_RANGE == "MAXIMUM_RANGE"
    assert OptimizationGoal.BALANCED_DESIGN == "BALANCED_DESIGN"


def test_optimization_stop_condition():
    """Verify OptimizationStopCondition evaluates max_iterations, min_improvement, and target_score thresholds."""
    cond = OptimizationStopCondition(max_iterations=5, min_improvement=0.01, target_score=0.95)

    # Below limits -> do not stop
    stop, _ = cond.should_stop(current_iteration=2, improvement_delta=0.05, current_best_score=0.80)
    assert not stop

    # Target score reached -> stop
    stop_score, reason1 = cond.should_stop(current_iteration=2, improvement_delta=0.05, current_best_score=0.96)
    assert stop_score
    assert "Target score threshold achieved" in reason1

    # Max iterations reached -> stop
    stop_iter, reason2 = cond.should_stop(current_iteration=5, improvement_delta=0.05, current_best_score=0.85)
    assert stop_iter
    assert "Maximum iterations limit reached" in reason2


def test_greedy_strategy_modifications():
    """Verify GreedyOptimizationStrategy generates modified candidate variants."""
    req = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=50.0
    )
    context = ContextBuilder.create_context(req)
    context.design_data = {
        "endurance_min": 30.0,
        "estimated_cost": 2000.0,
        "mtow_kg": 5.0,
        "payload_capacity_kg": 2.0,
        "thrust_to_weight_ratio": 2.0
    }

    candidate = OptimizationCandidate(design_context=context, iteration=0)
    strategy = GreedyOptimizationStrategy()

    variants = strategy.generate_modifications(candidate, iteration=1)

    assert len(variants) >= 3
    assert variants[0].iteration == 1
    assert variants[0].parent_candidate == candidate
    assert "endurance_min" in variants[0].design_context.design_data


def test_optimization_engine_execution():
    """Verify OptimizationEngine updates DesignContext stage to OPTIMIZATION and creates milestone snapshot."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=3.0,
        target_flight_time_min=35.0,
        target_range_km=25.0,
        cruise_speed_kmh=60.0
    )
    context = ContextBuilder.create_context(req)
    context.design_data = {
        "payload_capacity_kg": 3.0,
        "endurance_min": 35.0,
        "range_km": 25.0,
        "estimated_cost": 3000.0,
        "mtow_kg": 6.5,
        "thrust_to_weight_ratio": 2.1
    }

    engine = OptimizationEngine()
    updated_context = engine.optimize(context, max_iterations=3)

    assert updated_context.current_stage == DesignStage.OPTIMIZATION
    assert updated_context.current_status == DesignStatus.IN_PROGRESS
    assert len(updated_context.snapshots) == 2
    assert updated_context.snapshots[1].stage == DesignStage.OPTIMIZATION
