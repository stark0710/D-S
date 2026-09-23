"""
Phase 6B-1 Tests: OptimizationPriority Wiring and Propagation

Validates that:
1. OptimizationPriorityPolicy defines normalized, inspectable weights across all 9 optimizers.
2. OptimizationPriority propagates from RequirementModel to OptimizationContext and all subsystem optimizers.
3. Candidate scoring and selection respond to priority settings.
4. BALANCED preserves the protected baseline.
5. Hard constraints remain 100% hard across all priorities.
"""

import pytest
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.common.optimization.priority_policy import OptimizationPriorityPolicy
from backend.design.common.optimization.optimization_context import OptimizationContext

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus


def test_priority_policy_weight_normalization():
    """Verify that all weight configurations in OptimizationPriorityPolicy sum to 1.0."""
    for priority in OptimizationPriority:
        for getter in [
            OptimizationPriorityPolicy.get_wing_weights,
            OptimizationPriorityPolicy.get_fuselage_weights,
            OptimizationPriorityPolicy.get_payload_weights,
            OptimizationPriorityPolicy.get_tail_weights,
            OptimizationPriorityPolicy.get_electrical_weights,
            OptimizationPriorityPolicy.get_mass_weights,
            OptimizationPriorityPolicy.get_cg_weights,
            OptimizationPriorityPolicy.get_flight_performance_weights,
        ]:
            weights = getter(priority)
            assert abs(sum(weights.values()) - 1.0) < 1e-6, f"Weights for {getter.__name__} under {priority} do not sum to 1.0"

        # Propulsion with and without mission category
        for cat in [None, "Survey", "Cargo", "Racing"]:
            weights = OptimizationPriorityPolicy.get_propulsion_weights(priority, cat)
            assert abs(sum(weights.values()) - 1.0) < 1e-6, f"Propulsion weights under {priority} (cat={cat}) do not sum to 1.0"


def test_optimization_context_priority_propagation():
    """Verify that OptimizationContext correctly initializes or inherits optimization_priority."""
    # 1. Explicit passing
    ctx1 = OptimizationContext(requirements="mock", optimization_priority=OptimizationPriority.LOWEST_WEIGHT)
    assert ctx1.optimization_priority == OptimizationPriority.LOWEST_WEIGHT

    # 2. Inherited from raw_requirements
    class MockRaw:
        optimization_priority = OptimizationPriority.MAXIMUM_ENDURANCE

    class MockPipelineReqs:
        raw_requirements = MockRaw()

    ctx2 = OptimizationContext(requirements=MockPipelineReqs())
    assert ctx2.optimization_priority == OptimizationPriority.MAXIMUM_ENDURANCE


def test_hard_constraints_enforced_under_all_priorities():
    """Verify that impossible MTOW constraints are rejected regardless of OptimizationPriority."""
    for p in OptimizationPriority:
        req = RequirementModel(
            mission_type=MissionType.SURVEY,
            payload_weight_kg=2.0,
            maximum_takeoff_weight_kg=1.0,  # Impossible: limit < payload
            target_flight_time_min=45.0,
            target_range_km=30.0,
            cruise_speed_kmh=70.0,
            takeoff_type=TakeoffType.RUNWAY,
            landing_type=LandingType.RUNWAY,
            environment=OperatingEnvironment.RURAL,
            optimization_priority=p
        )
        res = FixedWingDesignPipeline().execute(req)
        assert res.success is False, f"Failed: Priority {p} accepted impossible MTOW"
        assert res.status == PipelineStatus.INVALID_REQUIREMENTS


def test_balanced_baseline_equivalence():
    """Verify that BALANCED produces the exact canonical baseline for Survey 0.5kg."""
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED
    )
    res = FixedWingDesignPipeline().execute(req)
    assert res.success is True
    mtow = res.final_specification.mass_properties.maximum_takeoff_weight_kg
    assert abs(mtow - 3.655) < 0.01, f"Expected 3.655 kg, got {mtow}"
    assert res.final_specification.wing.aspect_ratio == 10.0


def test_priority_sensitivity_cost_vs_weight():
    """Verify that LOWEST_COST selects a lower-complexity wing than BALANCED, and LOWEST_WEIGHT reduces MTOW."""
    pipeline = FixedWingDesignPipeline()

    req_cost = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.LOWEST_COST
    )
    res_cost = pipeline.execute(req_cost)
    assert res_cost.success is True
    assert res_cost.final_specification.wing.aspect_ratio == 8.0, "LOWEST_COST should select simpler AR=8 wing"
    assert res_cost.final_specification.mass_properties.maximum_takeoff_weight_kg < 3.655

    req_weight = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.LOWEST_WEIGHT
    )
    res_weight = pipeline.execute(req_weight)
    assert res_weight.success is True
    assert res_weight.final_specification.mass_properties.maximum_takeoff_weight_kg < 3.655, "LOWEST_WEIGHT should reduce MTOW"

