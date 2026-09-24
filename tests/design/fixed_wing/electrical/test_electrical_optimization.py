"""
Unit Tests for Fixed-Wing Electrical System & Component Integration Engine
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

from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements
from backend.design.fixed_wing.propulsion.optimization.models import PropulsionSpecification
from backend.design.fixed_wing.wing.optimization.models import WingPlanformSpecification
from backend.design.fixed_wing.fuselage.optimization.models import FuselageSpecification
from backend.design.fixed_wing.tail.optimization.models import TailSpecification

from backend.design.fixed_wing.electrical.models import ElectricalSystemSpecification
from backend.design.fixed_wing.electrical.result import ElectricalOptimizationResult
from backend.design.fixed_wing.electrical.candidate_generator import (
    ElectricalCandidateGenerator,
    build_electrical_repository,
)
from backend.design.fixed_wing.electrical.candidate_evaluator import CandidateEvaluator
from backend.design.fixed_wing.electrical.constraints import build_electrical_constraints
from backend.design.fixed_wing.electrical.objective_function import ElectricalObjectiveFunction
from backend.design.fixed_wing.electrical.electrical_optimizer import ElectricalOptimizer

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.components.component_category import ComponentCategory


@pytest.fixture
def mock_electrical_context():
    """Generates a mock OptimizationContext for electrical optimization testing."""
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
        maximum_takeoff_weight_kg=15.0,
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

    f_geom = FuselageGeometry(1.4, 0.22, 0.24, 0.25, 0.65, "Rectangular", 0.5, 1.4, 0.3, 0.15, 0.15, 0.005, 0.2, 0.15, 0.15, 0.002, 0.2, 0.15, 0.15, 0.04)
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

    from unittest.mock import MagicMock
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
        esc_name="80A BLHeli_32",
        battery_name="LiHV 12S 5000mAh 40C Pack",
        cell_count_s=12,
        battery_capacity_mah=5000.0,
        battery_weight_g=1232.4,
        total_propulsion_weight_g=1897.4,
        operating_voltage_v=45.6,
        cruise_current_a=14.5,
        max_climb_current_a=42.0,
        static_thrust_n=115.2,
        cruise_thrust_n=22.5,
        takeoff_power_w=1915.2,
        cruise_power_w=661.2,
        estimated_flight_time_min=80.0,
        motor_efficiency=0.85,
        propeller_efficiency=0.72,
        total_efficiency=0.61,
        optimization_score=0.82,
        reasoning="Mock propulsion spec",
    )

    return OptimizationContext(
        requirements=reqs,
        configuration=c_result,
        previous_specifications={
            "WingPlanformOptimizer": wing_spec,
            "FuselageOptimizer": fuse_spec,
            "TailOptimizer": tail_spec,
            "PropulsionOptimizer": prop_spec,
        },
    )


def test_electrical_component_repository():
    """Verify component database registers all required categories properly."""
    repo = build_electrical_repository()
    assert repo.count(ComponentCategory.FLIGHT_CONTROLLER) > 0
    assert repo.count(ComponentCategory.GPS) > 0
    assert repo.count(ComponentCategory.TELEMETRY) > 0
    assert repo.count(ComponentCategory.RECEIVER) > 0
    assert repo.count(ComponentCategory.SERVO) > 0
    assert repo.count(ComponentCategory.BEC) > 0
    assert repo.count(ComponentCategory.POWER_DISTRIBUTION_BOARD) > 0
    assert repo.count(ComponentCategory.PAYLOAD) > 0
    assert repo.count(ComponentCategory.SENSOR) > 0


def test_electrical_candidate_generation(mock_electrical_context):
    """Verify candidate generation creates feasible layouts matching constraints."""
    generator = ElectricalCandidateGenerator()
    candidates = generator.generate_candidates(mock_electrical_context)
    
    assert len(candidates) > 0
    for cand in candidates:
        assert cand.status == "PENDING"
        dv = cand.design_variables
        assert "flight_controller" in dv
        assert "gps" in dv
        assert "telemetry" in dv
        assert "receiver" in dv
        assert "servo" in dv
        assert "bec" in dv
        assert "power_module" in dv
        assert "mission_equipment" in dv


def test_electrical_constraints_evaluation(mock_electrical_context):
    """Verify constraints properly check candidate metrics."""
    generator = ElectricalCandidateGenerator()
    candidates = generator.generate_candidates(mock_electrical_context)
    
    evaluator = CandidateEvaluator()
    constraints = build_electrical_constraints()

    cand = candidates[0]
    evaluator.evaluate(cand, mock_electrical_context)

    # Check derived variables are populated
    assert "total_continuous_power_w" in cand.derived_variables
    assert "total_peak_current_a" in cand.derived_variables
    assert "wire_gauge_awg" in cand.derived_variables
    assert "connector_name" in cand.derived_variables
    assert "estimated_electrical_mass_g" in cand.derived_variables
    assert "redundancy_level" in cand.derived_variables

    # Verify constraint functions run
    for check in constraints:
        passed, reason = check(cand, mock_electrical_context)
        assert isinstance(passed, bool)


def test_electrical_objective_function(mock_electrical_context):
    """Verify the multi-objective score generates clean and bounded outputs."""
    generator = ElectricalCandidateGenerator()
    candidates = generator.generate_candidates(mock_electrical_context)
    
    evaluator = CandidateEvaluator()
    objective = ElectricalObjectiveFunction()

    cand = candidates[0]
    evaluator.evaluate(cand, mock_electrical_context)

    score = objective.evaluate(cand, mock_electrical_context)
    assert 0.0 <= score <= 1.0
    assert "reliability" in cand.objective_scores
    assert "power_margin" in cand.objective_scores
    assert "weight" in cand.objective_scores
    assert "cost" in cand.objective_scores


def test_electrical_optimizer_integration(mock_electrical_context):
    """Verify full optimization, spec building, and determinism."""
    optimizer = ElectricalOptimizer()
    result = optimizer.optimize(mock_electrical_context)

    assert isinstance(result, ElectricalOptimizationResult)
    assert result.success is True
    assert result.winning_candidate is not None
    assert isinstance(result.generated_specification, ElectricalSystemSpecification)

    spec = result.generated_specification
    assert len(spec.flight_controller_name) > 0
    assert len(spec.gps_name) > 0
    assert len(spec.telemetry_name) > 0
    assert len(spec.receiver_name) > 0
    assert len(spec.servo_name) > 0
    assert spec.servo_count > 0
    assert len(spec.bec_name) > 0
    assert len(spec.power_module_name) > 0
    assert isinstance(spec.wire_gauge_awg, int) and spec.wire_gauge_awg > 0
    assert len(spec.connector_type) > 0
    assert len(spec.mission_equipment_name) > 0

    assert spec.electrical_power_budget_w > 0.0
    assert spec.estimated_electrical_mass_g > 0.0
    assert spec.redundancy_level > 0
    assert spec.optimization_score > 0.0
    assert len(spec.reasoning) > 0

    # Determinism check
    result2 = optimizer.optimize(mock_electrical_context)
    assert result.winning_candidate.design_variables["flight_controller_name"] == \
           result2.winning_candidate.design_variables["flight_controller_name"]
