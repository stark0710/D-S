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
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

from backend.design.fixed_wing.wing.optimization.models import WingPlanformSpecification
from backend.design.fixed_wing.wing.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.wing.optimization.constraints import build_wing_constraints
from backend.design.fixed_wing.wing.optimization.objective_function import WingObjectiveFunction
from backend.design.fixed_wing.wing.optimization.wing_planform_optimizer import WingPlanformOptimizer

@pytest.fixture
def mock_wing_context():
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
    reqs = WingRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        metadata={"max_wingspan_m": 3.0}
    )
    return OptimizationContext(requirements=reqs, configuration=c_result)

def test_sprint22_candidate_generation(mock_wing_context):
    """Verify that candidate generator grid sweeps produce correct range and dimensions."""
    # Use smaller range steps for test speed
    gen = GridSearchCandidateGenerator(
        ar_range=(8.0, 10.0, 1.0),
        taper_range=(0.4, 0.5, 0.1),
        sweep_range=(0.0, 4.0, 2.0),
        dihedral_range=(0.0, 2.0, 1.0)
    )
    cands = gen.generate_candidates(mock_wing_context)
    # AR: 8,9,10 (3) * Taper: 0.4, 0.5 (2) * Sweep: 0, 2, 4 (3) * Dihedral: 0, 1, 2 (3) = 54 candidates
    assert len(cands) == 54
    assert cands[0].design_variables["aspect_ratio"] == 8.0
    assert cands[0].design_variables["wing_position"] == "High Wing"

def test_sprint22_constraints(mock_wing_context):
    """Verify pre-evaluation screening checks reject invalid geometries."""
    manager = build_wing_constraints()

    # 1. Invalid taper ratio
    cand_taper = OptimizationCandidate(design_variables={"taper_ratio": 0.2})
    assert manager.evaluate_constraints(cand_taper, mock_wing_context) is False

    # 2. Exceeding max wingspan span limits
    # S is ~0.5 m2, AR=16 => Span = sqrt(0.5 * 16) = 2.82 m < 3.0 m (PASS)
    # S is ~0.5 m2, AR=25 => Span = sqrt(0.5 * 25) = 3.53 m > 3.0 m (FAIL)
    cand_span = OptimizationCandidate(design_variables={"aspect_ratio": 25.0, "taper_ratio": 0.5})
    assert manager.evaluate_constraints(cand_span, mock_wing_context) is False

def test_sprint22_objective_function(mock_wing_context):
    """Verify that objective scoring weights are aggregated correctly."""
    from backend.design.fixed_wing.wing.wing_result import WingResult
    from backend.design.fixed_wing.wing.wing_geometry import WingGeometry

    geom = WingGeometry(
        span_m=2.0, area_m2=0.5, aspect_ratio=8.0, wing_loading_kg_m2=20.0,
        root_chord_m=0.3, tip_chord_m=0.2, taper_ratio=0.6, sweep_angle_deg=0.0,
        dihedral_angle_deg=0.0, wing_incidence_deg=0.0, mean_aerodynamic_chord_m=0.25,
        quarter_chord_x_m=0.06, reference_area_m2=0.5,
    )
    
    class DummyAnalysis:
        lift_coefficient_cruise = 0.5
        drag_coefficient_cruise = 0.05  # L/D = 10
        
    res = WingResult(
        wing_geometry=geom, planform="Tapered", reference_area=0.5, aspect_ratio=8.0,
        wing_loading=20.0, mean_aerodynamic_chord=0.25, quarter_chord_location=0.06,
        analysis=DummyAnalysis(), engineering_notes=["Estimated Wing weight: 0.8 kg."],
        recommendations=[], warnings=[],
        estimated_mtow_kg=5.0,
        estimated_wing_weight_kg=0.8,
    )
    
    cand = OptimizationCandidate(design_variables={"aspect_ratio": 8.0, "taper_ratio": 0.6, "sweep_angle_deg": 0.0})
    cand.derived_variables["wing_result"] = res
    cand.derived_variables["wing_span"] = 2.0

    obj = WingObjectiveFunction()
    score = obj.calculate_scores(cand, mock_wing_context)
    assert isinstance(score, float)
    assert cand.overall_score == score

def test_sprint22_optimizer_flow_and_determinism(mock_wing_context):
    """Verify optimizer runs the correct lifecycle and is deterministic."""
    # Restrict search bounds to speed up tests
    optimizer = WingPlanformOptimizer()
    optimizer.logger.info("Initializing search sweep test...")
    
    # We can inject a smaller search grid into optimizer for speed
    gen = GridSearchCandidateGenerator(
        ar_range=(8.0, 9.0, 1.0),
        taper_range=(0.4, 0.4, 0.1),
        sweep_range=(0.0, 0.0, 2.0),
        dihedral_range=(0.0, 0.0, 1.0)
    )
    # Temporarily override candidates list
    optimizer.generate_candidates = lambda ctx: gen.generate_candidates(ctx)

    # First run
    res1 = optimizer.optimize(mock_wing_context)
    assert res1.success is True
    assert res1.evaluated_count == 2
    assert res1.feasible_count > 0
    assert isinstance(res1.generated_specification, WingPlanformSpecification)
    
    spec = res1.generated_specification
    assert spec.wing_area > 0.0
    assert spec.wing_span > 0.0
    assert spec.root_chord >= 0.05
    assert spec.tip_chord >= 0.05
    
    # Second run for determinism
    res2 = optimizer.optimize(mock_wing_context)
    assert res2.success is True
    assert res2.winning_candidate.design_variables["aspect_ratio"] == res1.winning_candidate.design_variables["aspect_ratio"]
    assert res2.winning_candidate.overall_score == res1.winning_candidate.overall_score
