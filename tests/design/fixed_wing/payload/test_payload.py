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
from backend.design.fixed_wing.propulsion.thrust_analysis import ThrustAnalysis
from backend.design.fixed_wing.propulsion.power_analysis import PowerAnalysis as PropPowerAnalysis
from backend.design.fixed_wing.propulsion.efficiency_analysis import EfficiencyAnalysis
from backend.design.fixed_wing.propulsion.cruise_analysis import CruiseAnalysis as PropCruiseAnalysis
from backend.design.fixed_wing.propulsion.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.propulsion.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult
from backend.design.fixed_wing.avionics.navigation_analysis import NavigationAnalysis
from backend.design.fixed_wing.avionics.communication_analysis import CommunicationAnalysis
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis as AvPowerAnalysis
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult
from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements, PayloadType
from backend.design.fixed_wing.payload.payload_profile import PayloadProfile
from backend.design.fixed_wing.payload.payload_constraints import PayloadConstraints
from backend.design.fixed_wing.payload.payload_selector import PayloadSelector
from backend.design.fixed_wing.payload.payload_mount import PayloadMount
from backend.design.fixed_wing.payload.payload_layout import PayloadLayout
from backend.design.fixed_wing.payload.payload_power import PayloadPowerInterface
from backend.design.fixed_wing.payload.payload_data import PayloadDataInterface
from backend.design.fixed_wing.payload.payload_cooling import PayloadCooling
from backend.design.fixed_wing.payload.payload_analysis import PayloadAnalysis, PayloadAnalysisService
from backend.design.fixed_wing.payload.payload_validator import PayloadValidator, PayloadValidationError
from backend.design.fixed_wing.payload.payload_registry import PayloadStrategyRegistry
from backend.design.fixed_wing.payload.payload_strategy import CargoPayloadStrategy
from backend.design.fixed_wing.payload.payload_engine import PayloadEngine
from backend.design.fixed_wing.payload.payload_result import PayloadResult as PayloadEngineResult


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
        mission_range_km=15.0,
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
        minimum_range_km=15.0,
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

    f_geom = FuselageGeometry(1.5, 0.20, 0.40, 0.25, 0.6, "Rectangular", 0.5, 1.4, 0.3, 0.15, 0.15, 0.005, 0.2, 0.15, 0.15, 0.002, 0.2, 0.15, 0.15, 0.04)
    layout = InternalLayout(0, 0, 0, 0, 0, 0, 0, "", "", "duct", "")
    placement = ComponentPlacement(0.55, 0.55, 10.0, {}, {})
    interfaces = MountingInterfaces("", "", "", "", "", 0.0, 0.0, "")
    f_anal = FuselageAnalysis(80.0, 85.0, 90.0, 95.0, 80.0, 80.0, 0.18, "")
    f_result = FuselageResult(
        fuselage_geometry=f_geom,
        internal_layout=layout,
        component_placement=placement,
        mounting_interfaces=interfaces,
        fuselage_analysis=f_anal,
    )

    p_thrust = ThrustAnalysis(10.0, 30.0, 35.0, 0.55, 150.0)
    p_pow = PropPowerAnalysis(200.0, 450.0, 600.0, 15.0)
    p_ef = EfficiencyAnalysis(0.85, 0.70, 0.60, 4.0)
    p_cruise = PropCruiseAnalysis(80.0, 10.0, 5000.0, 50.0)
    p_climb = ClimbAnalysis(3.0, 10.0, 200.0, 2.0)
    p_takeoff = TakeoffAnalysis(20.0, 12.0, 15.0, 4.0)
    p_result = PropulsionResult(
        selected_motor_or_engine="SunnySky X2820",
        selected_propeller="12x6 APC",
        propulsion_layout="Single Tractor",
        thrust_analysis=p_thrust,
        power_analysis=p_pow,
        efficiency_analysis=p_ef,
        cruise_analysis=p_cruise,
        climb_analysis=p_climb,
        takeoff_analysis=p_takeoff,
    )

    av_nav = NavigationAnalysis("Standard", 1, True, False, 20.0)
    av_comm = CommunicationAnalysis(15.0, 64.0, True, 5.0)
    av_pow = AvPowerAnalysis(8.0, 10.0, False, 1.6)
    av_result = AvionicsResult(
        selected_flight_controller="Pixhawk 6C",
        selected_firmware="ArduPilot",
        selected_navigation_system="Standard GNSS",
        selected_receiver="ELRS",
        selected_telemetry="Sik Modem",
        selected_companion_computer="None",
        selected_sensors=["Airspeed Sensor"],
        navigation_analysis=av_nav,
        communication_analysis=av_comm,
        power_analysis=av_pow,
    )
    
    return m_result, c_result, w_result, a_result, t_result, f_result, p_result, av_result


def test_payload_selection():
    """Verify that payload selector picks correct cameras/sensors under weight thresholds."""
    selector = PayloadSelector()
    camera = selector.select_payload(PayloadType.RGB_CAMERA, max_weight_kg=1.0)
    assert camera.name == "Sony RX1R II (RGB)"
    assert camera.weight_kg == 0.51

    cargo = selector.select_payload(PayloadType.CARGO, max_weight_kg=3.0)
    assert cargo.payload_type == PayloadType.CARGO


def test_cg_shift_calculation():
    """Verify CG offset math."""
    service = PayloadAnalysisService()
    selector = PayloadSelector()
    camera = selector.select_payload(PayloadType.RGB_CAMERA, max_weight_kg=1.0)

    # If camera is placed exactly at CG: offset is 0, shift is 0
    anal = service.analyze_payload_integration(
        payloads=[camera],
        placement_x_m=0.50,
        cg_calculated_x_m=0.50,
        wing_mac=0.22,
        mtow_kg=10.0,
        compartment_vol=0.01,
    )
    assert anal.cg_shift_offset_m == 0.0
    assert anal.static_margin_impact_pct == 0.0

    # If camera is placed 10cm ahead of CG: offset is -0.1m, shift should be negative
    anal_shift = service.analyze_payload_integration(
        payloads=[camera],
        placement_x_m=0.40,
        cg_calculated_x_m=0.50,
        wing_mac=0.22,
        mtow_kg=10.0,
        compartment_vol=0.01,
    )
    # shift = (0.51 * -0.1) / 10.0 = -0.0051m = -5.1mm
    assert abs(anal_shift.cg_shift_offset_m - (-0.0051)) < 1e-4


def test_payload_strategy_selection():
    """Verify strategy registry fetches correct cargo strategies."""
    strategy = PayloadStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoPayloadStrategy)
    assert strategy.name == "Cargo"


def test_payload_validation_rules(dummy_engineering_results):
    """Test validator bounds for weight limits and excessive CG shifts."""
    m_result, c_result, w_result, a_result, t_result, f_result, p_result, av_result = dummy_engineering_results
    reqs = PayloadRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result, propulsion_result=p_result, avionics_result=av_result
    )

    constraints = PayloadConstraints(max_payload_weight_kg=1.0)
    profile = PayloadProfile(max_allowable_cg_offset_m=0.03)
    validator = PayloadValidator()

    anal = PayloadAnalysis(90.0, 10.0, 5.0, 0.01, 2.0, 1.2, 3.0, "Moderate", 90.0, "Summary")

    # Case 1: Payload weight exceeds constraints limit
    # Sized weight is 1.5kg, max is 1.0kg
    with pytest.raises(PayloadValidationError) as excinfo:
        validator.validate(reqs, constraints, profile, 1.5, 0.002, 0.01, anal)
    assert "payload weight" in str(excinfo.value)

    # Case 2: Excessive CG shift violates aerodynamic margin
    anal.cg_shift_offset_m = 0.045  # 45mm > 30mm limit
    with pytest.raises(PayloadValidationError) as excinfo:
        validator.validate(reqs, constraints, profile, 0.5, 0.002, 0.01, anal)
    assert "Center of Gravity displacement" in str(excinfo.value)


def test_payload_engine_flow(dummy_engineering_results):
    """Test full integration loop in PayloadEngine."""
    m_result, c_result, w_result, a_result, t_result, f_result, p_result, av_result = dummy_engineering_results
    reqs = PayloadRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result, propulsion_result=p_result, avionics_result=av_result
    )

    engine = PayloadEngine()
    result = engine.process_payload_design(reqs)

    assert isinstance(result, PayloadEngineResult)
    assert "Sony RX1R II (RGB)" in result.selected_payloads
    assert result.payload_layout.placement_x_m > 0.0
    assert len(result.payload_mounts) > 0
    assert result.payload_analysis.payload_accommodation_score > 0.0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
