"""
Unit Tests for Fixed-Wing Center of Gravity (CG) Optimization Engine
"""

import pytest
from unittest.mock import MagicMock
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

from backend.design.fixed_wing.propulsion.optimization.models import PropulsionSpecification
from backend.design.fixed_wing.wing.optimization.models import WingPlanformSpecification
from backend.design.fixed_wing.fuselage.optimization.models import FuselageSpecification
from backend.design.fixed_wing.tail.optimization.models import TailSpecification
from backend.design.fixed_wing.electrical.models import ElectricalSystemSpecification
from backend.design.fixed_wing.mass_properties.optimization.models import MassPropertiesSpecification
from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements

from backend.design.fixed_wing.cg.optimization.models import CGSpecification
from backend.design.fixed_wing.cg.optimization.result import CGOptimizationResult
from backend.design.fixed_wing.cg.optimization.candidate_generator import CGCandidateGenerator
from backend.design.fixed_wing.cg.optimization.candidate_evaluator import CGCandidateEvaluator
from backend.design.fixed_wing.cg.optimization.constraints import build_cg_constraints
from backend.design.fixed_wing.cg.optimization.objective_function import CGObjectiveFunction
from backend.design.fixed_wing.cg.optimization.cg_optimizer import CGOptimizer

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


@pytest.fixture
def mock_cg_context():
    """Generates a mock OptimizationContext for CG optimization testing."""
    profile = MissionProfile(
        mission_category=MissionCategory.MAPPING,
        payload_kg=1.5,
        flight_time_min=60.0,
        cruise_speed_kmh=80.0,
        stall_speed_target_kmh=35.0,
        maximum_takeoff_weight_limit_kg=12.0,
        operational_altitude_m=150.0,
        mission_range_km=25.0,
        launch_method=LaunchMethod.RUNWAY,
        landing_method=LandingMethod.RUNWAY,
        budget=12000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        air_density_kg_m3=1.2,
        energy_demand_kwh=0.8,
        cruise_emphasis=0.5,
        payload_emphasis=0.5,
        launch_recovery_complexity=0.3,
        environmental_complexity=0.2,
        operational_risk_score=0.4,
        mission_summary="Mock Mission Profile",
    )
    constraints = MissionConstraints(
        minimum_payload_kg=1.0,
        minimum_range_km=20.0,
        minimum_endurance_min=45.0,
        target_cruise_speed_kmh=80.0,
        maximum_stall_speed_kmh=40.0,
        maximum_takeoff_weight_kg=12.0,
        budget_limit=12000.0,
        required_launch_method=LaunchMethod.RUNWAY,
        required_landing_method=LandingMethod.RUNWAY,
        operating_environment=EnvironmentType.RURAL,
        required_autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    m_result = MissionResult(
        mission_profile=profile,
        mission_category=MissionCategory.MAPPING,
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
        configuration_score=90.0,
        wing_configuration="High Wing",
        propulsion_configuration="Tractor",
        tail_configuration="Conventional",
        landing_gear_configuration="Tricycle",
        engineering_rationale="Rationale",
        alternative_configurations=[],
    )
    wing_geom = WingGeometry(
        span_m=2.2, area_m2=0.48, aspect_ratio=10.0, wing_loading_kg_m2=25.0,
        root_chord_m=0.25, tip_chord_m=0.18, taper_ratio=0.72,
        sweep_angle_deg=0.0, dihedral_angle_deg=1.5, wing_incidence_deg=1.5,
        mean_aerodynamic_chord_m=0.22, quarter_chord_x_m=0.06, reference_area_m2=0.48,
    )
    wing_anal = WingAnalysis(
        wing_loading_rating="Good",
        lift_coefficient_cruise=0.48,
        estimated_stall_speed_kmh=36.0,
        aerodynamic_efficiency_score=85.0,
        structural_efficiency_score=82.0,
        manufacturability_score=90.0,
        stall_characteristics_rating="Mild",
        cruise_suitability=85.0,
        endurance_suitability=80.0,
        payload_suitability=80.0,
    )
    w_result = WingResult(
        wing_geometry=wing_geom, planform="Tapered", reference_area=0.48,
        aspect_ratio=10.0, wing_loading=25.0, mean_aerodynamic_chord=0.22,
        quarter_chord_location=0.06, analysis=wing_anal,
    )
    polar = PolarData(
        airfoil_name="Clark Y", cruise_cl=0.48, cruise_cd=0.012, cruise_l_d=40.0,
        max_l_d=45.0, max_l_d_cl=0.55, max_lift_coeff=1.4, stall_angle_deg=13.0,
        pitching_moment_c_m0=-0.06,
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

    f_geom = FuselageGeometry(1.4, 0.22, 0.24, 0.28, 0.65, "Rectangular", 0.5, 1.4, 0.3, 0.15, 0.15, 0.005, 0.2, 0.15, 0.15, 0.002, 0.2, 0.15, 0.15, 0.04)
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

    reqs = AvionicsRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        wing_result=w_result,
        airfoil_result=a_result,
        tail_result=t_result,
        fuselage_result=f_result,
        propulsion_result=MagicMock(),
    )

    wing_spec = WingPlanformSpecification(
        wing_span=2.2, wing_area=0.48, aspect_ratio=10.0,
        mac=0.22, taper_ratio=0.72, sweep=0.0, dihedral=1.5,
        root_chord=0.25, tip_chord=0.18, wing_loading=25.0,
        optimization_score=0.9, reasoning="Mock"
    )
    fuse_spec = FuselageSpecification(
        overall_length=1.4, width=0.22, height=0.24,
        nose_length=0.25, cabin_length=0.65, tail_cone_length=0.70,
        cross_section="Circular", fineness_ratio=6.4,
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
    prop_spec = PropulsionSpecification(
        motor_name="Generic Motor",
        propeller_name="Generic Prop",
        esc_name="Generic ESC",
        battery_name="Generic Battery",
        cell_count_s=6,
        battery_capacity_mah=5000.0,
        battery_weight_g=650.0,
        total_propulsion_weight_g=1050.0,
        operating_voltage_v=22.2,
        cruise_current_a=15.0,
        max_climb_current_a=40.0,
        static_thrust_n=100.0,
        cruise_thrust_n=20.0,
        takeoff_power_w=888.0,
        cruise_power_w=333.0,
        estimated_flight_time_min=60.0,
        motor_efficiency=0.85,
        propeller_efficiency=0.72,
        total_efficiency=0.61,
        optimization_score=0.82,
        reasoning="Mock",
    )
    elec_spec = ElectricalSystemSpecification(
        flight_controller_name="Cube", gps_name="GPS", compass_name="Compass",
        telemetry_name="Telemetry", receiver_name="Receiver", servo_name="Servo",
        servo_count=4, power_module_name="PM", bec_name="BEC",
        power_distribution_layout="Single Bus", wire_gauge_awg=14, connector_type="XT60",
        mission_equipment_name="Cam", electrical_power_budget_w=20.0,
        estimated_electrical_mass_g=350.0, redundancy_level=1, optimization_score=0.9,
        reasoning="Mock",
    )
    mass_spec = MassPropertiesSpecification(
        weight_breakdown={
            "wing": 1.344, "fuselage": 1.89, "horizontal_tail": 0.176, "vertical_tail": 0.132,
            "landing_gear": 0.54, "motor": 0.31, "propeller": 0.065, "esc": 0.08, "battery": 0.65,
            "flight_controller": 0.08, "gps": 0.05, "receiver": 0.01, "telemetry": 0.03,
            "power_module": 0.025, "bec": 0.015, "servos": 0.112, "mission_equipment": 0.5,
            "payload": 1.5, "fasteners": 0.106, "wiring": 0.12, "paint_finish": 0.0, "safety_margin": 0.298,
        },
        empty_weight_kg=5.888, operating_weight_kg=6.538, maximum_takeoff_weight_kg=8.538,
        payload_fraction=0.234, battery_fraction=0.076,
        subsystem_masses={"structure": 4.082, "propulsion": 0.455, "avionics": 0.322, "payload": 2.0, "battery": 0.65, "manufacturing": 0.226, "margin": 0.298},
        moments_of_inertia=(0.02, 0.45, 0.43),
        optimization_score=0.85, reasoning="Mock",
    )

    return OptimizationContext(
        requirements=reqs,
        configuration=c_result,
        previous_specifications={
            "WingPlanformOptimizer": wing_spec,
            "FuselageOptimizer": fuse_spec,
            "TailOptimizer": tail_spec,
            "PropulsionOptimizer": prop_spec,
            "ElectricalOptimizer": elec_spec,
            "MassPropertiesOptimizer": mass_spec,
        },
    )


def test_moment_and_cg_calculations(mock_cg_context):
    """Verify CG X/Y/Z coordinate solving and moments calculations."""
    cand = OptimizationCandidate(
        design_variables={
            "battery_pos_fraction": 0.35,
            "payload_pos_fraction": 0.40,
            "avionics_pos_fraction": 0.45,
        },
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    evaluator = CGCandidateEvaluator()
    evaluator.evaluate(cand, mock_cg_context)

    derived = cand.derived_variables
    assert "cg_position" in derived
    assert "neutral_point" in derived
    assert "static_margin" in derived
    assert "moment_summary" in derived

    cg = derived["cg_position"]
    moments = derived["moment_summary"]

    # CG must be within physical fuselage length [0, 1.4]
    assert 0.0 < cg[0] < 1.4
    assert cg[1] == 0.0  # lateral symmetry

    # Verify that moments equal mass * position sum
    total_mass = sum(c.mass_kg for c in derived["components"])
    total_moment = sum(moments.values())
    assert abs(total_moment - total_mass * cg[0]) < 1e-2


def test_static_stability_margin(mock_cg_context):
    """Verify that static stability margin matches standard formula exactly."""
    cand = OptimizationCandidate(
        design_variables={
            "battery_pos_fraction": 0.35,
            "payload_pos_fraction": 0.40,
            "avionics_pos_fraction": 0.45,
        },
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    evaluator = CGCandidateEvaluator()
    evaluator.evaluate(cand, mock_cg_context)

    derived = cand.derived_variables
    cg_x = derived["cg_position"][0]
    np_x = derived["neutral_point"]
    sm = derived["static_margin"]

    mac = mock_cg_context.requirements.wing_result.wing_geometry.mean_aerodynamic_chord_m
    expected_sm = (np_x - cg_x) / mac
    assert abs(sm - expected_sm) < 5e-3


def test_cg_constraints_validation(mock_cg_context):
    """Verify constraint checkers reject invalid/colliding components."""
    # Create a candidate where battery and payload occupy the exact same place (overlap)
    cand = OptimizationCandidate(
        design_variables={
            "battery_pos_fraction": 0.40,
            "payload_pos_fraction": 0.40,
            "avionics_pos_fraction": 0.70,
        },
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    
    constraints = build_cg_constraints()
    
    passed_overlap = True
    for check in constraints:
        if check.__name__ == "check_component_overlap":
            passed, reason = check(cand, mock_cg_context)
            passed_overlap = passed
            break
            
    assert passed_overlap is False


def test_cg_specification_and_diagnostics(mock_cg_context):
    """Verify optimizer builds specifications and yields full diagnostics properties."""
    optimizer = CGOptimizer()
    result = optimizer.optimize(mock_cg_context)

    assert isinstance(result, CGOptimizationResult)
    assert result.success is True
    assert result.winning_candidate is not None
    assert isinstance(result.generated_specification, CGSpecification)

    spec = result.generated_specification
    assert len(spec.cg_position) == 3
    assert spec.neutral_point > 0.0
    assert 0.10 <= spec.static_margin <= 0.20
    assert len(spec.component_positions) == 9
    assert len(spec.moment_summary) == 22
    assert len(spec.cg_envelope) == 3
    assert spec.optimization_score > 0.0
    assert len(spec.reasoning) > 0

    # Diagnostics checks
    diagnostics = result.diagnostics
    assert "initial_cg" in diagnostics
    assert "final_cg" in diagnostics
    assert "static_margin" in diagnostics
    assert "moved_components" in diagnostics
    assert "optimization_score" in diagnostics
    assert "execution_time" in diagnostics
