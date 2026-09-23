import pytest
import math
from backend.design.fixed_wing.mission.mission_requirements import (
    MissionRequirements,
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
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.wing.wing_engine import WingEngine

from backend.design.fixed_wing.optimization.optimization_models import PlanformCandidate, OptimizationBounds
from backend.design.fixed_wing.optimization.candidate_generator import (
    GridSearchCandidateGenerator,
    DeterministicRandomCandidateGenerator,
)
from backend.design.fixed_wing.optimization.optimization_constraints import OptimizationConstraints
from backend.design.fixed_wing.optimization.optimization_objective import WeightedMultiObjective
from backend.design.fixed_wing.optimization.wing_planform_optimizer import WingPlanformOptimizer

@pytest.fixture
def base_wing_requirements():
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
        mission_summary="Mapping mission",
    )
    constraints = MissionConstraints(
        minimum_payload_kg=2.0,
        minimum_range_km=40.0,
        minimum_endurance_min=60.0,
        target_cruise_speed_kmh=80.0,
        maximum_stall_speed_kmh=45.0,
        maximum_takeoff_weight_kg=10.0,
        budget_limit=10000.0,
        required_launch_method=LaunchMethod.CATAPULT,
        required_landing_method=LandingMethod.PARACHUTE,
        operating_environment=EnvironmentType.RURAL,
        required_autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    m_result = MissionResult(
        mission_profile=profile,
        mission_category=MissionCategory.SURVEY,
        mission_score=85.0,
        complexity="Medium",
        engineering_requirements={},
        constraints=constraints,
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
    return WingRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        preferred_planform=PlanformType.TAPERED,
        metadata={"max_wingspan_m": 3.0}
    )

def test_candidate_generators():
    """Verify aspect ratio, taper, sweep, and wing loading candidates are generated correctly."""
    bounds = OptimizationBounds(
        min_aspect_ratio=8.0,
        max_aspect_ratio=12.0,
        aspect_ratio_steps=3,
        min_taper_ratio=0.4,
        max_taper_ratio=0.6,
        taper_ratio_steps=2,
        min_sweep_deg=0.0,
        max_sweep_deg=10.0,
        sweep_steps=2,
        min_wing_loading_kg_m2=15.0,
        max_wing_loading_kg_m2=25.0,
        wing_loading_steps=2
    )

    # 1. Grid Search Generator: 3 * 2 * 2 * 2 = 24 candidates
    grid_gen = GridSearchCandidateGenerator()
    candidates = grid_gen.generate(bounds)
    assert len(candidates) == 24
    assert candidates[0].aspect_ratio == 8.0
    assert candidates[0].taper_ratio == 0.4
    assert candidates[-1].aspect_ratio == 12.0
    assert candidates[-1].taper_ratio == 0.6

    # 2. Deterministic Random Generator
    rand_gen = DeterministicRandomCandidateGenerator(sample_size=15, seed=42)
    rand_cands = rand_gen.generate(bounds)
    assert len(rand_cands) == 15

    # Determinism check
    rand_gen2 = DeterministicRandomCandidateGenerator(sample_size=15, seed=42)
    rand_cands2 = rand_gen2.generate(bounds)
    for c1, c2 in zip(rand_cands, rand_cands2):
        assert c1.aspect_ratio == c2.aspect_ratio
        assert c1.taper_ratio == c2.taper_ratio
        assert c1.sweep_angle_deg == c2.sweep_angle_deg
        assert c1.wing_loading_kg_m2 == c2.wing_loading_kg_m2

def test_optimization_constraints():
    """Verify constraint checks for wingspan, chords, and weight fraction limits."""
    geom = WingGeometry(
        span_m=4.0,  # exceeds max wingspan of 3.0 m
        area_m2=1.0,
        aspect_ratio=16.0,
        wing_loading_kg_m2=20.0,
        root_chord_m=0.3,
        tip_chord_m=0.02,  # below min chord of 0.05 m
        taper_ratio=0.06,
        sweep_angle_deg=10.0,
        dihedral_angle_deg=0.0,
        wing_incidence_deg=0.0,
        mean_aerodynamic_chord_m=0.2,
        quarter_chord_x_m=0.05,
        reference_area_m2=1.0,
    )
    result = WingResult(
        wing_geometry=geom,
        planform="Tapered",
        reference_area=1.0,
        aspect_ratio=16.0,
        wing_loading=20.0,
        mean_aerodynamic_chord=0.2,
        quarter_chord_location=0.05,
        analysis=None,
        engineering_notes=[
            "Estimated MTOW: 10.0 kg.",
            "Estimated Wing weight: 3.5 kg."  # wing fraction is 35% (> 25% limit)
        ],
        recommendations=[],
        warnings=[],
        estimated_mtow_kg=10.0,
        estimated_wing_weight_kg=3.5,
    )
    candidate = PlanformCandidate(16.0, 0.06, 10.0, 20.0)

    # Validate constraint checking
    cons = OptimizationConstraints(max_wingspan_m=3.0, min_chord_m=0.05, max_wing_mass_fraction=0.25)
    passed, violations = cons.check_constraints(candidate, result)
    
    assert passed is False
    assert len(violations) == 3
    assert any("Wingspan" in v for v in violations)
    assert any("Tip chord" in v for v in violations)
    assert any("Wing weight fraction" in v for v in violations)

def test_optimization_objective():
    """Verify scoring logic on structural weight, L/D ratio, and warnings count."""
    geom = WingGeometry(
        span_m=2.0,
        area_m2=0.5,
        aspect_ratio=8.0,
        wing_loading_kg_m2=20.0,
        root_chord_m=0.3,
        tip_chord_m=0.2,
        taper_ratio=0.6,
        sweep_angle_deg=0.0,
        dihedral_angle_deg=0.0,
        wing_incidence_deg=0.0,
        mean_aerodynamic_chord_m=0.25,
        quarter_chord_x_m=0.06,
        reference_area_m2=0.5,
    )
    
    class DummyAnalysis:
        lift_coefficient_cruise = 0.6
        drag_coefficient_cruise = 0.04  # L/D = 0.6 / 0.04 = 15.0
        
    result = WingResult(
        wing_geometry=geom,
        planform="Tapered",
        reference_area=0.5,
        aspect_ratio=8.0,
        wing_loading=20.0,
        mean_aerodynamic_chord=0.25,
        quarter_chord_location=0.06,
        analysis=DummyAnalysis(),
        engineering_notes=["Estimated Wing weight: 0.8 kg."],
        recommendations=[],
        warnings=["Soft warning 1", "Soft warning 2"],
        estimated_wing_weight_kg=0.8,
    )
    candidate = PlanformCandidate(8.0, 0.6, 0.0, 20.0)

    obj = WeightedMultiObjective(w_mass=10.0, w_ld=2.0, w_warnings=5.0)
    # Expected cost: 10.0 * 0.8 - 2.0 * 15.0 + 5.0 * 2 = 8.0 - 30.0 + 10.0 = -12.0
    score = obj.calculate_score(candidate, result)
    assert score == pytest.approx(-12.0)

def test_optimizer_flow_and_determinism(base_wing_requirements):
    """Verify that optimizer executes successfully and remains 100% deterministic."""
    bounds = OptimizationBounds(
        min_aspect_ratio=8.0,
        max_aspect_ratio=10.0,
        aspect_ratio_steps=2,
        min_taper_ratio=0.5,
        max_taper_ratio=0.5,
        taper_ratio_steps=1,
        min_sweep_deg=0.0,
        max_sweep_deg=0.0,
        sweep_steps=1,
        min_wing_loading_kg_m2=15.0,
        max_wing_loading_kg_m2=20.0,
        wing_loading_steps=2
    )

    optimizer = WingPlanformOptimizer()
    
    # 1. First execution
    res1 = optimizer.optimize(base_wing_requirements, bounds)
    assert res1.success is True
    assert res1.evaluated_count == 4
    assert res1.feasible_count > 0
    assert res1.best_candidate is not None

    # 2. Second execution (asserting determinism)
    res2 = optimizer.optimize(base_wing_requirements, bounds)
    assert res2.success is True
    assert res2.best_candidate.aspect_ratio == res1.best_candidate.aspect_ratio
    assert res2.best_candidate.wing_loading_kg_m2 == res1.best_candidate.wing_loading_kg_m2
    assert res2.best_candidate.taper_ratio == res1.best_candidate.taper_ratio
    assert res2.best_candidate.sweep_angle_deg == res1.best_candidate.sweep_angle_deg
