"""
Unit Tests for Fixed-Wing Mass Properties & Weight Build-up Engine
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
from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements

from backend.design.fixed_wing.mass_properties.optimization.models import MassPropertiesSpecification
from backend.design.fixed_wing.mass_properties.optimization.result import MassPropertiesOptimizationResult
from backend.design.fixed_wing.mass_properties.optimization.candidate_generator import MassCandidateGenerator
from backend.design.fixed_wing.mass_properties.optimization.candidate_evaluator import MassCandidateEvaluator
from backend.design.fixed_wing.mass_properties.optimization.constraints import build_mass_constraints
from backend.design.fixed_wing.mass_properties.optimization.objective_function import MassObjectiveFunction
from backend.design.fixed_wing.mass_properties.optimization.mass_optimizer import MassPropertiesOptimizer

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


@pytest.fixture
def mock_mass_context():
    """Generates a mock OptimizationContext for mass properties optimization testing."""
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
        motor_name="KDE Direct 7215XF",
        propeller_name="18x10 APC",
        esc_name="80A ESC",
        battery_name="LiHV 6S 5000mAh",
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
        flight_controller_name="Cube Orange+",
        gps_name="Here3",
        compass_name="Compass",
        telemetry_name="RFD900",
        receiver_name="ExpressLRS",
        servo_name="KST Servo",
        servo_count=4,
        power_module_name="PowerModule",
        bec_name="Matek BEC",
        power_distribution_layout="Single Bus",
        wire_gauge_awg=14,
        connector_type="XT60",
        mission_equipment_name="Survey Camera",
        electrical_power_budget_w=20.0,
        estimated_electrical_mass_g=350.0,
        redundancy_level=1,
        optimization_score=0.9,
        reasoning="Mock",
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
        },
    )


def test_mass_candidate_generation(mock_mass_context):
    """Verify that the candidate generator generates valid param sweeps."""
    generator = MassCandidateGenerator()
    candidates = generator.generate_candidates(mock_mass_context)
    assert len(candidates) > 0
    for cand in candidates:
        assert "structural_margin" in cand.design_variables
        assert "fastener_allowance" in cand.design_variables
        assert "paint_finish_type" in cand.design_variables
        assert "safety_growth_margin" in cand.design_variables


def test_mass_conservation_and_build_up(mock_mass_context):
    """Verify mass conservation: sum of individual items equals MTOW exactly."""
    cand = OptimizationCandidate(
        design_variables={
            "structural_margin": 1.05,
            "fastener_allowance": 0.03,
            "paint_finish_type": "Standard Paint",
            "safety_growth_margin": 0.05,
        },
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    evaluator = MassCandidateEvaluator()
    evaluator.evaluate(cand, mock_mass_context)

    derived = cand.derived_variables
    assert "mtow_kg" in derived
    assert "empty_weight_kg" in derived
    assert "operating_weight_kg" in derived
    assert "weight_breakdown" in derived

    # Test Mass Conservation: sum of all 22 components in breakdown
    breakdown = derived["weight_breakdown"]
    assert len(breakdown) == 22
    
    total_breakdown_mass = sum(breakdown.values())
    assert abs(total_breakdown_mass - derived["mtow_kg"]) < 1e-4


def test_fraction_calculations(mock_mass_context):
    """Verify weight fraction calculations are mathematically accurate."""
    cand = OptimizationCandidate(
        design_variables={
            "structural_margin": 1.0,
            "fastener_allowance": 0.03,
            "paint_finish_type": "None",
            "safety_growth_margin": 0.05,
        },
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    evaluator = MassCandidateEvaluator()
    evaluator.evaluate(cand, mock_mass_context)

    derived = cand.derived_variables
    mtow = derived["mtow_kg"]
    
    # fractions
    payload_frac = derived["payload_fraction"]
    battery_frac = derived["battery_fraction"]
    struct_frac = derived["structural_fraction"]

    subsystem = derived["subsystem_masses"]
    
    assert abs(payload_frac - round(subsystem["payload"] / mtow, 3)) < 1e-4
    assert abs(battery_frac - round(subsystem["battery"] / mtow, 3)) < 1e-4
    assert abs(struct_frac - round(subsystem["structure"] / mtow, 3)) < 1e-4


def test_constraint_validation(mock_mass_context):
    """Verify constraint checks reject infeasible cases."""
    cand = OptimizationCandidate(
        design_variables={
            "structural_margin": 1.10,
            "fastener_allowance": 0.05,
            "paint_finish_type": "Standard Paint",
            "safety_growth_margin": 0.10,
        },
        derived_variables={},
        objective_scores={},
        status="PENDING",
    )
    
    # Artificially set constraints limit very low to force MTOW exceedance
    mock_mass_context.requirements.mission_result.constraints.maximum_takeoff_weight_kg = 2.0

    constraints = build_mass_constraints()
    
    # Run MTOW check
    passed_mtow = False
    for check in constraints:
        if check.__name__ == "check_mtow_limit":
            passed, reason = check(cand, mock_mass_context)
            passed_mtow = passed
            break
            
    assert passed_mtow is False


def test_specification_and_diagnostics(mock_mass_context):
    """Verify complete optimizer runs, creates specification, and populates diagnostics."""
    optimizer = MassPropertiesOptimizer()
    result = optimizer.optimize(mock_mass_context)

    assert isinstance(result, MassPropertiesOptimizationResult)
    assert result.success is True
    assert result.winning_candidate is not None
    assert isinstance(result.generated_specification, MassPropertiesSpecification)

    spec = result.generated_specification
    assert spec.empty_weight_kg > 0.0
    assert spec.operating_weight_kg > 0.0
    assert spec.maximum_takeoff_weight_kg > 0.0
    assert spec.payload_fraction > 0.0
    assert spec.battery_fraction > 0.0
    assert len(spec.weight_breakdown) == 22
    assert len(spec.subsystem_masses) > 0
    assert len(spec.moments_of_inertia) == 3
    assert spec.optimization_score > 0.0
    assert len(spec.reasoning) > 0

    # Diagnostics checks
    diagnostics = result.diagnostics
    assert "weight_breakdown" in diagnostics
    assert "subsystem_summary" in diagnostics
    assert "constraint_summary" in diagnostics
    assert "optimization_score" in diagnostics
    assert "execution_time" in diagnostics
