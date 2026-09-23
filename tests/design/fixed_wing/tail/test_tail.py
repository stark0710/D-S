import pytest
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
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_analysis import WingAnalysis
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.airfoil.polar_analysis import PolarData
from backend.design.fixed_wing.airfoil.performance_map import PerformanceMap
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysis
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
from backend.design.fixed_wing.tail.tail_profile import TailProfile
from backend.design.fixed_wing.tail.tail_constraints import TailConstraints
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.control_surface import ControlSurfaces
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysisService, TailAnalysis
from backend.design.fixed_wing.tail.tail_validator import TailValidator, TailValidationError
from backend.design.fixed_wing.tail.tail_registry import TailStrategyRegistry
from backend.design.fixed_wing.tail.tail_strategy import CargoTailStrategy
from backend.design.fixed_wing.tail.tail_sizer import TailSizer
from backend.design.fixed_wing.tail.tail_engine import TailEngine
from backend.design.fixed_wing.tail.tail_result import TailResult as TailEngineResult


@pytest.fixture
def dummy_engineering_results():
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
    
    wing_geom = WingGeometry(
        span_m=2.0,
        area_m2=0.4,
        aspect_ratio=10.0,
        wing_loading_kg_m2=20.0,
        root_chord_m=0.25,
        tip_chord_m=0.15,
        taper_ratio=0.6,
        sweep_angle_deg=0.0,
        dihedral_angle_deg=2.0,
        wing_incidence_deg=2.0,
        mean_aerodynamic_chord_m=0.22,
        quarter_chord_x_m=0.08,
        reference_area_m2=0.4,
    )
    wing_anal = WingAnalysis(
        wing_loading_rating="Moderate",
        lift_coefficient_cruise=0.45,
        estimated_stall_speed_kmh=42.0,
        aerodynamic_efficiency_score=80.0,
        structural_efficiency_score=85.0,
        manufacturability_score=90.0,
        stall_characteristics_rating="Good",
        cruise_suitability=80.0,
        endurance_suitability=80.0,
        payload_suitability=80.0,
    )
    w_result = WingResult(
        wing_geometry=wing_geom,
        planform="Tapered",
        reference_area=0.4,
        aspect_ratio=10.0,
        wing_loading=20.0,
        mean_aerodynamic_chord=0.22,
        quarter_chord_location=0.08,
        analysis=wing_anal,
    )
    
    polar = PolarData(
        airfoil_name="Clark Y",
        cruise_cl=0.45,
        cruise_cd=0.010,
        cruise_l_d=45.0,
        max_l_d=50.0,
        max_l_d_cl=0.5,
        max_lift_coeff=1.35,
        stall_angle_deg=14.0,
        pitching_moment_c_m0=-0.05,
    )
    perf_map = PerformanceMap("Clark Y", [], [], [], [])
    reynolds = ReynoldsAnalysis(0, 0, 0, 0, 0, "")
    a_result = AirfoilResult(
        selected_root_airfoil="Clark Y",
        selected_tip_airfoil="NACA 0012",
        airfoil_distribution="",
        polar_data=polar,
        performance_map=perf_map,
        reynolds_analysis=reynolds,
    )
    
    return m_result, c_result, w_result, a_result


def test_tail_arm_sizing():
    """Verify tail arm distance estimation proportional to wingspan."""
    sizer = TailSizer()
    arm_conv = sizer.size_tail_arm(span_m=3.0, tail_style=TailConfigType.CONVENTIONAL, default_ratio=0.6)
    assert arm_conv == pytest.approx(1.8)

    arm_tailless = sizer.size_tail_arm(span_m=3.0, tail_style=TailConfigType.TAILLESS, default_ratio=0.6)
    assert arm_tailless == 0.0


def test_stabilizer_areas_sizing():
    """Verify horizontal and vertical tail area sizing from volume coefficients."""
    sizer = TailSizer()
    s_h, s_v = sizer.size_stabilizer_areas(
        wing_area_m2=1.0,
        mac_m=0.3,
        span_m=3.0,
        tail_arm_m=1.8,
        target_v_h=0.5,
        target_v_v=0.04,
        tail_style=TailConfigType.CONVENTIONAL,
    )
    # S_h = (0.5 * 1.0 * 0.3) / 1.8 = 0.0833
    assert s_h == pytest.approx(0.0833, abs=1e-4)
    # S_v = (0.04 * 1.0 * 3.0) / 1.8 = 0.0667
    assert s_v == pytest.approx(0.0667, abs=1e-4)


def test_control_surfaces_sizing():
    """Test control surfaces span and chord ratios sizing."""
    sizer = TailSizer()
    h_tail, v_tail = sizer.generate_geometry(
        horizontal_area=0.1,
        vertical_area=0.08,
        horiz_ar=4.0,
        vert_ar=2.0,
        horiz_sweep=0.0,
        horiz_taper=0.7,
        vert_sweep=15.0,
        vert_taper=0.6,
        tail_style=TailConfigType.CONVENTIONAL,
    )
    controls = sizer.size_control_surfaces(
        h_tail=h_tail, v_tail=v_tail, elevator_ratio=0.30, rudder_ratio=0.30, tail_style=TailConfigType.CONVENTIONAL
    )
    assert controls.elevator_span_m == h_tail.span_m
    assert controls.elevator_area_m2 == pytest.approx(h_tail.area_m2 * 0.30, abs=1e-4)
    assert controls.rudder_height_m == v_tail.height_m
    assert controls.rudder_area_m2 == pytest.approx(v_tail.area_m2 * 0.30, abs=1e-4)


def test_tail_volume_calculations():
    """Verify stability volume coefficients output calculations."""
    service = TailAnalysisService()
    analysis = service.analyze_tail_performance(
        wing_area_m2=1.0,
        mac_m=0.3,
        span_m=3.0,
        horizontal_area_m2=0.1,
        vertical_area_m2=0.08,
        tail_arm_m=1.8,
        tail_style="Conventional",
        elevator_chord_ratio=0.3,
        rudder_chord_ratio=0.3,
    )
    # V_h = (0.1 * 1.8) / (1.0 * 0.3) = 0.60
    assert analysis.horizontal_volume_coefficient == 0.60
    # V_v = (0.08 * 1.8) / (1.0 * 3.0) = 0.048
    assert analysis.vertical_volume_coefficient == 0.048


def test_tail_strategy_selection():
    """Verify tail strategy registry matches concrete strategists."""
    strategy = TailStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoTailStrategy)
    assert strategy.name == "Cargo"


def test_tail_validation_rules(dummy_engineering_results):
    """Verify stability bounds and airfoil pitching moment balancing."""
    m_result, c_result, w_result, a_result = dummy_engineering_results
    reqs = TailRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result
    )
    
    constraints = TailConstraints(
        min_v_h=0.35,
        max_v_h=1.0,
        min_v_v=0.02,
        max_v_v=0.09,
    )
    
    validator = TailValidator()
    
    h_tail = HorizontalTail(0.08, 0.5, 0.18, 0.14, 4.0, 0.0, 0.7, 0.0)
    v_tail = VerticalTail(0.06, 0.4, 0.16, 0.12, 2.0, 20.0, 0.6)
    controls = ControlSurfaces(0.5, 0.3, 0.024, 25.0, 70.0, 0.4, 0.3, 0.018, 30.0, 70.0)
    
    analysis = TailAnalysis(
        horizontal_volume_coefficient=0.30,  # Below 0.35
        vertical_volume_coefficient=0.04,
        pitch_stability_rating="",
        yaw_stability_rating="",
        pitch_control_authority=80.0,
        yaw_control_authority=80.0,
        trim_capability="",
        structural_simplicity_score=90.0,
        manufacturability_score=90.0,
        mission_suitability=80.0,
    )
    
    # Case 1: Low Volume V_h violates constraint
    with pytest.raises(TailValidationError) as excinfo:
        validator.validate(reqs, constraints, TailConfigType.CONVENTIONAL, h_tail, v_tail, controls, analysis)
    assert "Horizontal tail volume coefficient" in str(excinfo.value)

    # Case 2: High camber pitching moment airfoil with insufficient V_h
    a_result.polar_data.pitching_moment_c_m0 = -0.12  # High camber
    analysis.horizontal_volume_coefficient = 0.38    # Too low for -0.12
    with pytest.raises(TailValidationError) as excinfo:
        validator.validate(reqs, constraints, TailConfigType.CONVENTIONAL, h_tail, v_tail, controls, analysis)
    assert "High-camber root airfoil has pitching moment" in str(excinfo.value)


def test_tail_engine_flow(dummy_engineering_results):
    """Test full integration loop in TailEngine."""
    m_result, c_result, w_result, a_result = dummy_engineering_results
    reqs = TailRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result
    )
    
    engine = TailEngine()
    result = engine.process_tail_design(reqs)
    
    assert isinstance(result, TailEngineResult)
    assert result.tail_configuration == "Conventional"
    assert result.horizontal_tail.area_m2 > 0.0
    assert result.vertical_tail.area_m2 > 0.0
    assert result.control_surfaces.elevator_area_m2 > 0.0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
