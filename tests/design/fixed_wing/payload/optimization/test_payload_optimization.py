import pytest
from backend.design.fixed_wing.mission.mission_requirements import (
    MissionCategory,
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
)
from backend.design.fixed_wing.mission.mission_constraints import MissionConstraints
from backend.design.fixed_wing.mission.mission_profile import MissionProfile
from backend.design.fixed_wing.mission.mission_result import MissionResult
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult
from backend.design.fixed_wing.fuselage.optimization.models import FuselageSpecification
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

from backend.design.fixed_wing.payload.optimization.models import PayloadPackagingSpecification
from backend.design.fixed_wing.payload.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.payload.optimization.constraints import build_payload_constraints
from backend.design.fixed_wing.payload.optimization.objective_function import PayloadObjectiveFunction
from backend.design.fixed_wing.payload.optimization.payload_optimizer import PayloadPackagingOptimizer

@pytest.fixture
def mock_payload_context():
    # Mock fuselage specification
    fuse_spec = FuselageSpecification(
        overall_length=1.3,
        width=0.20,
        height=0.20,
        nose_length=0.23,
        cabin_length=0.55,
        tail_cone_length=0.52,
        cross_section="Circular",
        fineness_ratio=8.0,
        wing_mount_position=0.416,  # Wing spar is at 0.416 m
        payload_bay={},
        battery_bay={},
        avionics_bay={},
        bulkhead_locations=[],
        optimization_score=0.9,
        reasoning="Mock"
    )
    
    profile = MissionProfile(
        mission_category=MissionCategory.SURVEY,
        payload_kg=2.0,
        flight_time_min=60.0,
        cruise_speed_kmh=80.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=10.0,
        operational_altitude_m=150.0,
        mission_range_km=40.0,
        launch_method=LaunchMethod.CATAPULT,
        landing_method=LandingMethod.PARACHUTE,
        budget=10000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        air_density_kg_m3=1.2,
        energy_demand_kwh=0.5,
        cruise_emphasis=0.7,
        payload_emphasis=0.3,
        launch_recovery_complexity=0.5,
        environmental_complexity=0.3,
        operational_risk_score=0.4,
        mission_summary="Survey mission",
    )
    m_result = MissionResult(
        mission_profile=profile,
        mission_category=MissionCategory.SURVEY,
        mission_score=85.0,
        complexity="Medium",
        engineering_requirements={},
        constraints=None,
        recommendations=[],
        warnings=[],
        metadata={},
    )
    c_result = ConfigurationResult(
        selected_configuration={
            "wing_position": "High Wing",
            "propulsion_layout": "Tractor",
            "tail_configuration": "Conventional",
            "landing_gear_configuration": "Tricycle",
        },
        configuration_score=85.0,
        wing_configuration="High Wing",
        propulsion_configuration="Tractor",
        tail_configuration="Conventional",
        landing_gear_configuration="Tricycle",
        engineering_rationale="Rationale",
        alternative_configurations=[],
    )
    
    reqs = FuselageRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        wing_result=None,
        airfoil_result=None,
        tail_result=None
    )
    
    return OptimizationContext(
        requirements=reqs,
        configuration=c_result,
        previous_specifications={"FuselageOptimizer": fuse_spec}
    )

def test_sprint24_candidate_generation(mock_payload_context):
    """Verify that candidate generator produces correct packaging strategies."""
    gen = GridSearchCandidateGenerator()
    cands = gen.generate_candidates(mock_payload_context)
    # 3 payload * 3 battery positions = 9, minus p_pos == b_pos (3) = 6 layouts
    # 6 layouts * 2 battery orientations * 3 electronics layouts = 36 candidates
    assert len(cands) == 36
    assert cands[0].design_variables["payload_position_mode"] in ["Forward", "Mid", "Rear"]

def test_sprint24_overlap_and_spar_constraints(mock_payload_context):
    """Verify component overlap and wing spar collision checking."""
    manager = build_payload_constraints()
    
    # 1. Overlapping payload and battery (both at Mid)
    # Note: Generator filters p_pos == b_pos, but let's test manual construction
    cand_overlap = OptimizationCandidate(
        design_variables={
            "payload_position_mode": "Mid",
            "battery_position_mode": "Mid",
            "battery_orientation": "Longitudinal",
            "electronics_layout_mode": "Stacked Above"
        }
    )
    assert manager.evaluate_constraints(cand_overlap, mock_payload_context) is False

    # 2. Wing spar collision
    # wing_mount_position is at 0.416 m
    # If payload is Mid: nose_l (0.23) + 0.50 * cabin_l (0.55) = 0.505 m
    # Payload boundaries: [0.505 - 0.075, 0.505 + 0.075] = [0.430, 0.580] m
    # wing_mount is 0.416, which is outside [0.43, 0.58], so it passes.
    # If payload is Forward: nose_l (0.23) + 0.15 * cabin_l (0.55) = 0.3125 m
    # Payload boundaries: [0.3125 - 0.075, 0.3125 + 0.075] = [0.2375, 0.3875] m
    # wing_mount is 0.416, which is outside [0.2375, 0.3875], so it passes.
    
    # Let's test a case where payload directly intersects wing spar (e.g. wing_mount_position = 0.35)
    fuse_spec_bad = mock_payload_context.previous_specifications["FuselageOptimizer"]
    object.__setattr__(fuse_spec_bad, "wing_mount_position", 0.35)
    
    cand_spar = OptimizationCandidate(
        design_variables={
            "payload_position_mode": "Forward",
            "battery_position_mode": "Rear",
            "battery_orientation": "Longitudinal",
            "electronics_layout_mode": "Stacked Above"
        }
    )
    assert manager.evaluate_constraints(cand_spar, mock_payload_context) is False

def test_sprint24_objective_function(mock_payload_context):
    """Verify weighted multi-objective scoring for payload packaging."""
    cand = OptimizationCandidate(
        design_variables={
            "payload_position_mode": "Forward",
            "battery_position_mode": "Rear",
            "battery_orientation": "Longitudinal",
            "electronics_layout_mode": "Side Mounted"
        }
    )
    cand.derived_variables["packing_efficiency"] = 0.82
    
    obj = PayloadObjectiveFunction()
    score = obj.calculate_scores(cand, mock_payload_context)
    assert isinstance(score, float)
    assert cand.overall_score == score

def test_sprint24_optimizer_flow_and_determinism(mock_payload_context):
    """Verify optimizer lifecycle is clean, correct, and deterministic."""
    # Reset wing spar position to safe
    fuse_spec = mock_payload_context.previous_specifications["FuselageOptimizer"]
    object.__setattr__(fuse_spec, "wing_mount_position", 0.416)

    optimizer = PayloadPackagingOptimizer()
    res1 = optimizer.optimize(mock_payload_context)
    
    assert res1.success is True
    assert res1.evaluated_count > 0
    assert res1.feasible_count > 0
    assert isinstance(res1.generated_specification, PayloadPackagingSpecification)
    
    spec = res1.generated_specification
    assert spec.payload_position > 0
    assert spec.battery_position > 0
    
    # Second run to assert determinism
    res2 = optimizer.optimize(mock_payload_context)
    assert res2.success is True
    assert res2.winning_candidate.design_variables == res1.winning_candidate.design_variables
    assert res2.winning_candidate.overall_score == res1.winning_candidate.overall_score
