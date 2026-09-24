"""
Unit Tests for Fixed-Wing Flight Performance Sizer/Optimizer
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
from backend.design.fixed_wing.cg.optimization.models import CGSpecification

from backend.design.fixed_wing.performance.optimization.models import FlightPerformanceSpecification
from backend.design.fixed_wing.performance.optimization.result import FlightPerformanceOptimizationResult
from backend.design.fixed_wing.performance.optimization.candidate_generator import FlightPerformanceCandidateGenerator
from backend.design.fixed_wing.performance.optimization.candidate_evaluator import FlightPerformanceCandidateEvaluator
from backend.design.fixed_wing.performance.optimization.constraints import build_performance_constraints
from backend.design.fixed_wing.performance.optimization.objective_function import FlightPerformanceObjectiveFunction
from backend.design.fixed_wing.performance.optimization.performance_engine import FlightPerformanceOptimizer

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class DummyObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def mock_performance_context():
    """Generates an OptimizationContext for Performance Sizing tests."""
    profile = MissionProfile(
        mission_category=MissionCategory.SURVEY,
        payload_kg=1.2,
        flight_time_min=30.0,
        cruise_speed_kmh=75.0,
        stall_speed_target_kmh=50.0,
        maximum_takeoff_weight_limit_kg=10.0,
        operational_altitude_m=120.0,
        mission_range_km=20.0,
        launch_method=LaunchMethod.RUNWAY,
        landing_method=LandingMethod.RUNWAY,
        budget=12000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        air_density_kg_m3=1.2,
        energy_demand_kwh=0.20,
        cruise_emphasis=0.5,
        payload_emphasis=0.5,
        launch_recovery_complexity=0.3,
        environmental_complexity=0.2,
        operational_risk_score=0.4,
        mission_summary="Mock Mission Profile",
    )
    constraints = MissionConstraints(
        minimum_payload_kg=1.0,
        minimum_range_km=15.0,
        minimum_endurance_min=30.0,
        target_cruise_speed_kmh=75.0,
        maximum_stall_speed_kmh=52.0,
        maximum_takeoff_weight_kg=10.0,
        budget_limit=12000.0,
        required_launch_method=LaunchMethod.RUNWAY,
        required_landing_method=LandingMethod.RUNWAY,
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
        configuration_score=90.0,
        wing_configuration="High Wing",
        propulsion_configuration="Tractor",
        tail_configuration="Conventional",
        landing_gear_configuration="Tricycle",
        engineering_rationale="Rationale",
        alternative_configurations=[],
    )
    wing_geom = WingGeometry(
        span_m=2.0, area_m2=0.45, aspect_ratio=8.89, wing_loading_kg_m2=17.78,
        root_chord_m=0.25, tip_chord_m=0.20, taper_ratio=0.8,
        sweep_angle_deg=0.0, dihedral_angle_deg=1.5, wing_incidence_deg=1.5,
        mean_aerodynamic_chord_m=0.22, quarter_chord_x_m=0.06, reference_area_m2=0.45,
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
        wing_geometry=wing_geom, planform="Tapered", reference_area=0.45,
        aspect_ratio=8.89, wing_loading=17.78, mean_aerodynamic_chord=0.22,
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

    f_geom = FuselageGeometry(1.2, 0.22, 0.24, 0.24, 0.54, "Rectangular", 0.48, 1.15, 0.3, 0.15, 0.15, 0.005, 0.2, 0.15, 0.15, 0.002, 0.2, 0.15, 0.15, 0.04)
    layout = InternalLayout(0, 0, 0, 0, 0, 0, 0, "", "", "duct", "")
    placement = ComponentPlacement(0.55, 0.55, 8.0, {}, {})
    interfaces = MountingInterfaces("", "", "", "", "", 0.0, 0.0, "")
    f_anal = FuselageAnalysis(82.0, 85.0, 88.0, 92.0, 80.0, 80.0, 0.18, "")
    f_result = FuselageResult(
        fuselage_geometry=f_geom,
        internal_layout=layout,
        component_placement=placement,
        mounting_interfaces=interfaces,
        fuselage_analysis=f_anal,
    )

    from unittest.mock import MagicMock
    reqs = DummyObject(
        mission_result=m_result,
        configuration_result=c_result,
        wing_result=w_result,
        airfoil_result=a_result,
        tail_result=t_result,
        fuselage_result=f_result,
        propulsion_result=MagicMock(),
    )

    wing_spec = WingPlanformSpecification(
        wing_span=2.0, wing_area=0.45, aspect_ratio=8.89,
        mac=0.22, taper_ratio=0.8, sweep=0.0, dihedral=1.5,
        root_chord=0.25, tip_chord=0.20, wing_loading=17.78,
        optimization_score=0.9, reasoning="Mock"
    )
    fuse_spec = FuselageSpecification(
        overall_length=1.2, width=0.22, height=0.24,
        nose_length=0.24, cabin_length=0.42, tail_cone_length=0.54,
        cross_section="Rectangular", fineness_ratio=5.0,
        wing_mount_position=0.4, payload_bay={}, battery_bay={},
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
        battery_weight_g=800.0,
        total_propulsion_weight_g=1200.0,
        operating_voltage_v=22.2,
        cruise_current_a=12.0,
        max_climb_current_a=35.0,
        static_thrust_n=100.0,
        cruise_thrust_n=20.0,
        takeoff_power_w=800.0,
        cruise_power_w=260.0,
        estimated_flight_time_min=60.0,
        motor_efficiency=0.85,
        propeller_efficiency=0.72,
        total_efficiency=0.61,
        optimization_score=0.85,
        reasoning="Mock",
    )
    elec_spec = ElectricalSystemSpecification(
        flight_controller_name="Cube", gps_name="GPS", compass_name="Compass",
        telemetry_name="Telemetry", receiver_name="Receiver", servo_name="Servo",
        servo_count=4, power_module_name="PM", bec_name="BEC",
        power_distribution_layout="Single Bus", wire_gauge_awg=14, connector_type="XT60",
        mission_equipment_name="Cam", electrical_power_budget_w=15.0,
        estimated_electrical_mass_g=350.0, redundancy_level=1, optimization_score=0.9,
        reasoning="Mock",
    )
    mass_spec = MassPropertiesSpecification(
        weight_breakdown={
            "wing": 1.26, "fuselage": 1.62, "horizontal_tail": 0.176, "vertical_tail": 0.132,
            "landing_gear": 0.32, "motor": 0.31, "propeller": 0.065, "esc": 0.08, "battery": 0.80,
            "flight_controller": 0.08, "gps": 0.05, "receiver": 0.01, "telemetry": 0.03,
            "power_module": 0.025, "bec": 0.015, "servos": 0.112, "mission_equipment": 0.5,
            "payload": 1.2, "fasteners": 0.106, "wiring": 0.12, "paint_finish": 0.02, "safety_margin": 0.3,
        },
        empty_weight_kg=5.202, operating_weight_kg=6.002, maximum_takeoff_weight_kg=8.002,
        payload_fraction=0.15, battery_fraction=0.10,
        subsystem_masses={"structure": 3.508, "propulsion": 0.455, "avionics": 0.322, "payload": 1.7, "battery": 0.8, "manufacturing": 0.226, "margin": 0.3},
        moments_of_inertia=(0.02, 0.45, 0.43),
        optimization_score=0.85, reasoning="Mock",
    )
    cg_spec = CGSpecification(
        cg_position=(0.55, 0.0, 0.0), neutral_point=0.65, static_margin=0.15,
        component_positions={}, moment_summary={}, cg_envelope={},
        optimization_score=0.9, reasoning="Mock",
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
            "CGOptimizer": cg_spec,
        },
    )


def test_performance_evaluations(mock_performance_context):
    """Verify primary flight predictions (stall speed, range, endurance, takeoff, landing)."""
    cand = OptimizationCandidate(
        design_variables={},
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    evaluator = FlightPerformanceCandidateEvaluator()
    evaluator.evaluate(cand, mock_performance_context)

    derived = cand.derived_variables
    assert "stall_speed" in derived
    assert "cruise_speed" in derived
    assert "maximum_speed" in derived
    assert "takeoff_distance" in derived
    assert "landing_distance" in derived
    assert "rate_of_climb" in derived
    assert "range" in derived
    assert "endurance" in derived

    assert derived["stall_speed"] > 0.0
    assert derived["takeoff_distance"] > 0.0
    assert derived["landing_distance"] > 0.0
    assert derived["rate_of_climb"] > 0.0
    assert derived["range"] > 0.0
    assert derived["endurance"] > 0.0


def test_performance_constraints_validation(mock_performance_context):
    """Verify constraint checks correctly validate performance margins."""
    cand = OptimizationCandidate(
        design_variables={},
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    
    constraints = build_performance_constraints()
    for check in constraints:
        passed, reason = check(cand, mock_performance_context)
        # Sized mock aircraft must pass all safety constraints successfully
        assert passed is True, f"Constraint {check.__name__} failed: {reason}"


def test_performance_specification_and_diagnostics(mock_performance_context):
    """Verify optimizer builds specifications and yields full diagnostics properties."""
    optimizer = FlightPerformanceOptimizer()
    result = optimizer.optimize(mock_performance_context)

    assert isinstance(result, FlightPerformanceOptimizationResult)
    assert result.success is True
    assert result.winning_candidate is not None
    assert isinstance(result.generated_specification, FlightPerformanceSpecification)

    spec = result.generated_specification
    assert spec.stall_speed_kmh > 0.0
    assert spec.takeoff_distance_m > 0.0
    assert spec.landing_distance_m > 0.0
    assert spec.range_km > 0.0
    assert spec.endurance_min > 0.0
    assert spec.power_required_w > 0.0
    assert spec.power_available_w > 0.0
    assert spec.performance_score > 0.0
    assert len(spec.reasoning) > 0

    # Diagnostics checks
    diagnostics = result.diagnostics
    assert "performance_summary" in diagnostics
    assert "mission_compliance" in diagnostics
    assert "constraint_summary" in diagnostics
    assert "power_summary" in diagnostics
    assert "execution_time" in diagnostics
    assert "performance_score" in diagnostics
