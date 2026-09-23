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
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

from backend.design.fixed_wing.fuselage.optimization.models import FuselageSpecification
from backend.design.fixed_wing.fuselage.optimization.candidate_generator import GridSearchCandidateGenerator
from backend.design.fixed_wing.fuselage.optimization.constraints import build_fuselage_constraints
from backend.design.fixed_wing.fuselage.optimization.objective_function import FuselageObjectiveFunction
from backend.design.fixed_wing.fuselage.optimization.fuselage_optimizer import FuselageOptimizer

@pytest.fixture
def mock_fuselage_context():
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
    w_geom = WingGeometry(
        span_m=2.0, area_m2=0.5, aspect_ratio=8.0, wing_loading_kg_m2=20.0,
        root_chord_m=0.3, tip_chord_m=0.2, taper_ratio=0.6, sweep_angle_deg=0.0,
        dihedral_angle_deg=0.0, wing_incidence_deg=0.0, mean_aerodynamic_chord_m=0.25,
        quarter_chord_x_m=0.06, reference_area_m2=0.5,
    )
    w_res = WingResult(
        wing_geometry=w_geom, planform="Tapered", reference_area=0.5, aspect_ratio=8.0,
        wing_loading=20.0, mean_aerodynamic_chord=0.25, quarter_chord_location=0.06,
        analysis=None, engineering_notes=[], recommendations=[], warnings=[]
    )
    t_res = TailResult(
        tail_configuration="Conventional",
        horizontal_tail=None,
        vertical_tail=None,
        control_surfaces=None,
        tail_volume_coefficients={},
        tail_analysis=None,
        engineering_notes=[],
        recommendations=[],
        warnings=[]
    )
    reqs = FuselageRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        wing_result=w_res,
        airfoil_result=None,
        tail_result=t_res
    )
    return OptimizationContext(requirements=reqs, configuration=c_result)

def test_sprint23_candidate_generation(mock_fuselage_context):
    """Verify that candidate generator grid sweeps produce correct range and dimensions."""
    gen = GridSearchCandidateGenerator(
        length_range=(1.0, 2.0, 0.5),
        width_range=(0.10, 0.20, 0.05),
        height_range=(0.10, 0.20, 0.05),
        fineness_range=(6.0, 8.0, 2.0),
        cross_sections=["Circular"]
    )
    cands = gen.generate_candidates(mock_fuselage_context)
    # L: 1.0, 1.5, 2.0 (3) * W: 0.10, 0.15, 0.20 (3) * H: 0.10, 0.15, 0.20 (3) * FR: 6.0, 8.0 (2) * CS: Circular (1) = 54 candidates
    assert len(cands) == 54
    assert cands[0].design_variables["length"] == 1.0
    assert cands[0].design_variables["bulkhead_locations"] == [0.0, 0.18, 0.6, 1.0]

def test_sprint23_constraints(mock_fuselage_context):
    """Verify pre-evaluation screening checks reject invalid geometries."""
    manager = build_fuselage_constraints()

    # 1. Invalid payload width (width too small)
    cand_width = OptimizationCandidate(
        design_variables={
            "length": 1.5, "width": 0.05, "height": 0.2, "fineness_ratio": 8.0, "cross_section": "Circular",
            "nose_length": 0.27, "tail_cone_length": 0.6
        }
    )
    assert manager.evaluate_constraints(cand_width, mock_fuselage_context) is False

    # 2. Too short tail arm
    # span is 2.0m, required tail arm is 0.6m.
    # length=0.6m => wing_attach=0.192, tail_attach=0.57 => arm = 0.378m < 0.6m (FAIL)
    cand_arm = OptimizationCandidate(
        design_variables={
            "length": 0.6, "width": 0.3, "height": 0.3, "fineness_ratio": 8.0, "cross_section": "Circular",
            "nose_length": 0.108, "tail_cone_length": 0.24
        }
    )
    assert manager.evaluate_constraints(cand_arm, mock_fuselage_context) is False

def test_sprint23_objective_function(mock_fuselage_context):
    """Verify that objective scoring weights are aggregated correctly."""
    from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult
    from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
    from backend.design.fixed_wing.fuselage.component_placement import ComponentPlacement
    from backend.design.fixed_wing.fuselage.fuselage_analysis import FuselageAnalysis

    geom = FuselageGeometry(
        length_m=1.5, width_m=0.2, height_m=0.2, nose_length_m=0.27, tail_cone_length_m=0.6,
        cross_section_type="Circular", wing_attachment_x_m=0.48, tail_attachment_x_m=1.425,
        payload_bay_length_m=0.33, payload_bay_width_m=0.17, payload_bay_height_m=0.15, payload_bay_volume_m3=0.0084,
        battery_bay_length_m=0.24, battery_bay_width_m=0.17, battery_bay_height_m=0.11, battery_bay_volume_m3=0.0045,
        avionics_bay_length_m=0.21, avionics_bay_width_m=0.17, avionics_bay_height_m=0.07, total_volume_m3=0.045
    )
    
    placement = ComponentPlacement(
        calculated_cg_x_m=0.53, target_cg_x_m=0.53, static_margin_pct=15.0,
        component_locations={}, component_masses={}
    )
    
    analysis = FuselageAnalysis(
        packaging_efficiency_score=80.0,
        payload_accommodation_score=85.0,
        aerodynamic_efficiency_score=90.0,
        manufacturability_score=95.0,
        component_accessibility_score=85.0,
        cooling_adequacy_score=80.0,
        volume_utilization_ratio=0.65,
        analysis_summary="Summary"
    )

    res = FuselageResult(
        fuselage_geometry=geom, internal_layout=None, component_placement=placement,
        mounting_interfaces=None, fuselage_analysis=analysis, engineering_notes=[],
        recommendations=[], warnings=[]
    )
    
    cand = OptimizationCandidate(
        design_variables={
            "length": 1.5, "width": 0.2, "height": 0.2, "fineness_ratio": 7.5, "cross_section": "Circular",
            "nose_length": 0.27, "tail_cone_length": 0.6, "bulkhead_locations": [0, 0.27, 0.9, 1.5]
        }
    )
    cand.derived_variables["fuselage_result"] = res

    obj = FuselageObjectiveFunction()
    score = obj.calculate_scores(cand, mock_fuselage_context)
    assert isinstance(score, float)
    assert cand.overall_score == score

def test_sprint23_optimizer_flow_and_determinism(mock_fuselage_context):
    """Verify optimizer runs the correct lifecycle and is deterministic."""
    optimizer = FuselageOptimizer()
    
    # Restrict candidate search size for test speed
    gen = GridSearchCandidateGenerator(
        length_range=(1.5, 1.6, 0.5),
        width_range=(0.20, 0.20, 0.05),
        height_range=(0.20, 0.20, 0.05),
        fineness_range=(8.0, 8.0, 2.0),
        cross_sections=["Circular"]
    )
    optimizer.generate_candidates = lambda ctx: gen.generate_candidates(ctx)

    # First run
    res1 = optimizer.optimize(mock_fuselage_context)
    assert res1.success is True
    assert res1.evaluated_count == 1
    assert res1.feasible_count == 1
    assert isinstance(res1.generated_specification, FuselageSpecification)
    
    spec = res1.generated_specification
    assert spec.overall_length == 1.5
    assert spec.width == 0.20
    assert spec.height == 0.20
    assert spec.cross_section == "Circular"
    
    # Second run for determinism
    res2 = optimizer.optimize(mock_fuselage_context)
    assert res2.success is True
    assert res2.winning_candidate.design_variables["length"] == res1.winning_candidate.design_variables["length"]
    assert res2.winning_candidate.overall_score == res1.winning_candidate.overall_score
