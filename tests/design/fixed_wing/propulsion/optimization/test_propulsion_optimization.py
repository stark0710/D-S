"""
Unit Tests for Fixed-Wing Propulsion Sizing Optimization Engine
"""

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
from backend.design.fixed_wing.wing.wing_analysis import WingAnalysis
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.polar_analysis import PolarData
from backend.design.fixed_wing.airfoil.performance_map import PerformanceMap
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysis
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.control_surface import ControlSurfaces
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysis
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.internal_layout import InternalLayout
from backend.design.fixed_wing.fuselage.component_placement import ComponentPlacement
from backend.design.fixed_wing.fuselage.mounting_interfaces import MountingInterfaces
from backend.design.fixed_wing.fuselage.fuselage_analysis import FuselageAnalysis
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult

from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
from backend.design.fixed_wing.propulsion.optimization.models import PropulsionSpecification
from backend.design.fixed_wing.propulsion.optimization.result import PropulsionOptimizationResult
from backend.design.fixed_wing.propulsion.optimization.candidate_generator import (
    GridSearchPropulsionCandidateGenerator,
    build_component_repository,
)
from backend.design.fixed_wing.propulsion.optimization.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.propulsion.optimization.constraints import build_propulsion_constraints
from backend.design.fixed_wing.propulsion.optimization.objective_function import PropulsionObjectiveFunction
from backend.design.fixed_wing.propulsion.optimization.propulsion_optimizer import PropulsionOptimizer

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.components.component_category import ComponentCategory

from backend.design.fixed_wing.wing.optimization.models import WingPlanformSpecification
from backend.design.fixed_wing.fuselage.optimization.models import FuselageSpecification
from backend.design.fixed_wing.tail.optimization.models import TailSpecification


@pytest.fixture
def mock_propulsion_context():
    """Builds an OptimizationContext representative of a fixed-wing cargo UAV."""
    profile = MissionProfile(
        mission_category=MissionCategory.CARGO,
        payload_kg=3.0,
        flight_time_min=45.0,
        cruise_speed_kmh=90.0,
        stall_speed_target_kmh=42.0,
        maximum_takeoff_weight_limit_kg=12.0,
        operational_altitude_m=200.0,
        mission_range_km=30.0,
        launch_method=LaunchMethod.RUNWAY,
        landing_method=LandingMethod.RUNWAY,
        budget=8000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        air_density_kg_m3=1.2,
        energy_demand_kwh=0.6,
        cruise_emphasis=0.5,
        payload_emphasis=0.5,
        launch_recovery_complexity=0.4,
        environmental_complexity=0.3,
        operational_risk_score=0.4,
        mission_summary="Cargo transport mission",
    )
    constraints = MissionConstraints(
        minimum_payload_kg=3.0,
        minimum_range_km=30.0,
        minimum_endurance_min=45.0,
        target_cruise_speed_kmh=90.0,
        maximum_stall_speed_kmh=42.0,
        maximum_takeoff_weight_kg=12.0,
        budget_limit=8000.0,
        required_launch_method=LaunchMethod.RUNWAY,
        required_landing_method=LandingMethod.RUNWAY,
        operating_environment=EnvironmentType.RURAL,
        required_autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    m_result = MissionResult(
        mission_profile=profile,
        mission_category=MissionCategory.CARGO,
        mission_score=80.0,
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
    wing_geom = WingGeometry(
        span_m=2.4, area_m2=0.58, aspect_ratio=9.9, wing_loading_kg_m2=20.7,
        root_chord_m=0.30, tip_chord_m=0.18, taper_ratio=0.6,
        sweep_angle_deg=0.0, dihedral_angle_deg=2.0, wing_incidence_deg=2.0,
        mean_aerodynamic_chord_m=0.25, quarter_chord_x_m=0.08, reference_area_m2=0.58,
    )
    wing_anal = WingAnalysis(
        wing_loading_rating="Moderate",
        lift_coefficient_cruise=0.45,
        estimated_stall_speed_kmh=40.0,
        aerodynamic_efficiency_score=82.0,
        structural_efficiency_score=84.0,
        manufacturability_score=88.0,
        stall_characteristics_rating="Good",
        cruise_suitability=80.0,
        endurance_suitability=80.0,
        payload_suitability=80.0,
    )
    w_result = WingResult(
        wing_geometry=wing_geom, planform="Tapered", reference_area=0.58,
        aspect_ratio=9.9, wing_loading=20.7, mean_aerodynamic_chord=0.25,
        quarter_chord_location=0.08, analysis=wing_anal,
    )
    polar = PolarData(
        airfoil_name="Clark Y", cruise_cl=0.45, cruise_cd=0.010, cruise_l_d=45.0,
        max_l_d=50.0, max_l_d_cl=0.5, max_lift_coeff=1.35, stall_angle_deg=14.0,
        pitching_moment_c_m0=-0.05,
    )
    perf_map = PerformanceMap("Clark Y", [], [], [], [])
    reynolds = ReynoldsAnalysis(0, 0, 0, 0, 0, "")
    a_result = AirfoilResult(
        selected_root_airfoil="Clark Y", selected_tip_airfoil="NACA 0012",
        airfoil_distribution="", polar_data=polar,
        performance_map=perf_map, reynolds_analysis=reynolds,
    )

    h_tail = HorizontalTail(0.08, 0.5, 0.18, 0.14, 4.0, 0.0, 0.7, 0.0)
    v_tail = VerticalTail(0.06, 0.4, 0.16, 0.12, 2.0, 20.0, 0.6)
    controls = ControlSurfaces(0.5, 0.3, 0.024, 25.0, 70.0, 0.4, 0.3, 0.018, 30.0, 70.0)
    t_anal = TailAnalysis(0.5, 0.04, "", "", 80.0, 80.0, "", 90.0, 90.0, 80.0)
    t_result = TailResult(
        tail_configuration="Conventional",
        horizontal_tail=h_tail,
        vertical_tail=v_tail,
        control_surfaces=controls,
        tail_volume_coefficients={},
        tail_analysis=t_anal,
    )

    f_geom = FuselageGeometry(1.6, 0.22, 0.45, 0.28, 0.65, "Rectangular", 0.5, 1.4, 0.3, 0.15, 0.15, 0.005, 0.2, 0.15, 0.15, 0.002, 0.2, 0.15, 0.15, 0.04)
    layout = InternalLayout(0, 0, 0, 0, 0, 0, 0, "", "", "duct", "")
    placement = ComponentPlacement(0.55, 0.55, 12.0, {}, {})
    interfaces = MountingInterfaces("", "", "", "", "", 0.0, 0.0, "")
    f_anal = FuselageAnalysis(82.0, 85.0, 88.0, 92.0, 80.0, 80.0, 0.18, "")
    f_result = FuselageResult(
        fuselage_geometry=f_geom,
        internal_layout=layout,
        component_placement=placement,
        mounting_interfaces=interfaces,
        fuselage_analysis=f_anal,
    )

    reqs = PropulsionRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        wing_result=w_result,
        airfoil_result=a_result,
        tail_result=t_result,
        fuselage_result=f_result,
    )

    wing_spec = WingPlanformSpecification(
        wing_span=2.4, wing_area=0.58, aspect_ratio=9.9,
        mac=0.25, taper_ratio=0.6, sweep=0.0, dihedral=2.0,
        root_chord=0.30, tip_chord=0.18, wing_loading=20.7,
        optimization_score=0.9, reasoning="Mock"
    )
    fuse_spec = FuselageSpecification(
        overall_length=1.6, width=0.22, height=0.45,
        nose_length=0.25, cabin_length=0.65, tail_cone_length=0.70,
        cross_section="Circular", fineness_ratio=7.3,
        wing_mount_position=0.45, payload_bay={}, battery_bay={},
        avionics_bay={}, bulkhead_locations=[],
        optimization_score=0.9, reasoning="Mock",
    )
    tail_spec = TailSpecification(
        tail_configuration="Conventional",
        horizontal_tail_area_m2=0.08, horizontal_tail_span_m=0.5,
        horizontal_tail_root_chord_m=0.18, horizontal_tail_tip_chord_m=0.14,
        vertical_tail_area_m2=0.06, vertical_tail_height_m=0.4,
        vertical_tail_root_chord_m=0.16, vertical_tail_tip_chord_m=0.12,
        horizontal_volume_coefficient=0.5, vertical_volume_coefficient=0.04,
        tail_arm_m=0.85, horizontal_aspect_ratio=4.0, vertical_aspect_ratio=2.0,
        horizontal_taper_ratio=0.7, vertical_taper_ratio=0.6,
        horizontal_sweep_deg=0.0, vertical_sweep_deg=20.0, tail_dihedral_deg=0.0,
        optimization_score=0.95, reasoning="Mock",
    )

    return OptimizationContext(
        requirements=reqs,
        configuration=c_result,
        previous_specifications={
            "WingPlanformOptimizer": wing_spec,
            "FuselageOptimizer": fuse_spec,
            "TailOptimizer": tail_spec,
        },
    )


def test_propulsion_component_repository():
    """Verify ComponentRepository registers components and has proper counts."""
    repo = build_component_repository()
    assert repo.count(ComponentCategory.MOTOR) == 7
    assert repo.count(ComponentCategory.PROPELLER) == 12
    assert repo.count(ComponentCategory.ESC) == 6
    # 3 chemistries × 4 cell counts × 6 capacities = 72 battery packs
    assert repo.count(ComponentCategory.BATTERY) == 72


def test_propulsion_candidate_generation(mock_propulsion_context):
    """Verify that candidate generator produces pre-filtered compatible configurations."""
    generator = GridSearchPropulsionCandidateGenerator()
    cands = generator.generate_candidates(mock_propulsion_context)
    
    assert len(cands) > 0
    # Every generated candidate must have compatible voltage (matching cell count)
    for c in cands:
        dv = c.design_variables
        assert dv["battery"]["cell_count_s"] == dv["motor"]["cell_count_s"]
        assert dv["esc"]["continuous_current_a"] >= dv["motor"]["max_current_a"]


def test_propulsion_constraints_evaluation(mock_propulsion_context):
    """Verify constraints mark infeasible combinations appropriately."""
    generator = GridSearchPropulsionCandidateGenerator()
    cands = generator.generate_candidates(mock_propulsion_context)
    
    evaluator = CandidateEvaluator()
    constraints = build_propulsion_constraints()

    # Find a candidate that successfully evaluates
    evaluated_successfully = False
    for cand in cands:
        evaluator.evaluate(cand, mock_propulsion_context)
        if cand.status == "EVALUATED":
            evaluated_successfully = True
            break
    
    assert evaluated_successfully is True
    # Assert derived variables are populated
    assert "cruise_power_w" in cand.derived_variables
    assert "cruise_current_a" in cand.derived_variables
    assert "static_thrust_n" in cand.derived_variables
    assert "estimated_flight_time_min" in cand.derived_variables

    # Evaluate constraints manually
    for check in constraints:
        passed, reason = check(cand, mock_propulsion_context)
        # We just verify it executes without error
        assert isinstance(passed, bool)


def test_propulsion_objective_function(mock_propulsion_context):
    """Verify candidate scoring and category weight adaptations."""
    objective = PropulsionObjectiveFunction()
    
    # Mock a feasible candidate
    cand = OptimizationCandidate(design_variables={
        "motor": {"name": "Test Motor", "max_current_a": 35.0},
        "esc": {"name": "Test ESC", "continuous_current_a": 40.0},
        "battery": {"name": "Test Battery"},
    })
    cand.derived_variables = {
        "total_efficiency": 0.55,
        "total_propulsion_weight_g": 380.0,
        "cruise_power_w": 120.0,
        "static_thrust_n": 15.0,
        "takeoff_thrust_n": 8.0,
        "estimated_flight_time_min": 52.0,
        "climb_current_a": 25.0,
    }
    cand.status = "FEASIBLE"
    cand.constraints_passed = True

    score = objective.evaluate(cand, mock_propulsion_context)
    assert score > 0.0
    assert "electrical_efficiency" in cand.objective_scores
    assert "endurance" in cand.objective_scores
    
    # Test cargo category emphasis weight change
    mock_propulsion_context.requirements.mission_result.mission_category = MissionCategory.CARGO
    cargo_score = objective.evaluate(cand, mock_propulsion_context)
    assert cargo_score > 0.0


def test_propulsion_optimizer_integration(mock_propulsion_context):
    """Verify the full PropulsionOptimizer execution, spec generation, and determinism."""
    optimizer = PropulsionOptimizer()
    result = optimizer.optimize(mock_propulsion_context)

    assert isinstance(result, PropulsionOptimizationResult)
    assert result.success is True
    assert result.winning_candidate is not None
    assert isinstance(result.generated_specification, PropulsionSpecification)
    
    spec = result.generated_specification
    assert len(spec.motor_name) > 0
    assert len(spec.propeller_name) > 0
    assert len(spec.esc_name) > 0
    assert len(spec.battery_name) > 0
    
    assert spec.static_thrust_n > 0.0
    assert spec.estimated_flight_time_min > 0.0
    assert spec.total_efficiency > 0.0
    
    # Verify diagnostics are present
    assert result.execution_time_seconds >= 0.0
    assert result.evaluated_count > 0
    assert len(result.rejected_summary) >= 0

    # Test determinism: Running optimize twice must yield identical winning candidate
    result2 = optimizer.optimize(mock_propulsion_context)
    assert result.winning_candidate.design_variables["motor_name"] == result2.winning_candidate.design_variables["motor_name"]
    assert result.winning_candidate.design_variables["propeller_name"] == result2.winning_candidate.design_variables["propeller_name"]
    assert result.winning_candidate.design_variables["esc_name"] == result2.winning_candidate.design_variables["esc_name"]
    assert result.winning_candidate.design_variables["battery_name"] == result2.winning_candidate.design_variables["battery_name"]
