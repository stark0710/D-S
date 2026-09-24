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
from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements, AutopilotFirmware, GNSSConfiguration
from backend.design.fixed_wing.avionics.avionics_profile import AvionicsProfile
from backend.design.fixed_wing.avionics.avionics_constraints import AvionicsConstraints
from backend.design.fixed_wing.avionics.flight_controller_selector import FlightControllerSelector
from backend.design.fixed_wing.avionics.gps_selector import GPSSelector
from backend.design.fixed_wing.avionics.receiver_selector import ReceiverSelector
from backend.design.fixed_wing.avionics.telemetry_selector import TelemetrySelector
from backend.design.fixed_wing.avionics.camera_selector import CameraSelector
from backend.design.fixed_wing.avionics.companion_computer_selector import CompanionComputerSelector
from backend.design.fixed_wing.avionics.sensor_selector import SensorSelector
from backend.design.fixed_wing.avionics.navigation_analysis import NavigationAnalysis
from backend.design.fixed_wing.avionics.communication_analysis import CommunicationAnalysis
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis
from backend.design.fixed_wing.avionics.avionics_validator import AvionicsValidator, AvionicsValidationError
from backend.design.fixed_wing.avionics.avionics_registry import AvionicsStrategyRegistry
from backend.design.fixed_wing.avionics.avionics_strategy import CargoAvionicsStrategy
from backend.design.fixed_wing.avionics.avionics_engine import AvionicsEngine
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult as AvionicsEngineResult


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
    
    return m_result, c_result, w_result, a_result, t_result, f_result, p_result


def test_fc_selection():
    """Verify that flight controller selector finds appropriate triple redundant boards."""
    selector = FlightControllerSelector()
    fc = selector.select_flight_controller(needs_redundancy=True, needs_ethernet=False)
    assert fc.name in ("Cube Orange+", "Holybro Pixhawk 6X")
    assert fc.triple_redundant


def test_gps_selection():
    """Verify GNSS selector handles RTK accuracy constraints."""
    selector = GPSSelector()
    gps_rtk = selector.select_gps(needs_rtk=True, needs_dual=True)
    assert gps_rtk.supports_rtk
    assert gps_rtk.supports_dual


def test_receiver_selection():
    """Verify RC receiver select matches range envelopes."""
    selector = ReceiverSelector()
    rx = selector.select_receiver(target_range_km=15.0)
    assert rx.typical_range_km >= 15.0


def test_telemetry_selection():
    """Verify telemetry link selector matches video bandwidth targets."""
    selector = TelemetrySelector()
    telem = selector.select_telemetry(target_range_km=15.0, needs_video=True)
    assert telem.max_bandwidth_kbps >= 1000.0
    assert telem.max_range_km >= 15.0


def test_companion_computer_selection():
    """Test SBC processors lookup matches image processing visual nav needs."""
    selector = CompanionComputerSelector()
    sbc = selector.select_companion_computer(needs_visual_nav=True, needs_high_ai=True)
    assert sbc is not None
    assert sbc.ai_tops >= 40.0


def test_sensor_package_selection():
    """Verify sensor selector fetches airspeed sensors and compasses."""
    selector = SensorSelector()
    sensors = selector.select_sensors("Cargo")
    names = [s.name for s in sensors]
    assert "Holybro Digital Airspeed Sensor" in names
    assert "LightWare SF11/C Laser Altimeter" in names  # heavy cargo lidar


def test_avionics_strategy_selection():
    """Verify registry matches strategies."""
    strategy = AvionicsStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoAvionicsStrategy)
    assert strategy.name == "Cargo"


def test_avionics_validation_rules(dummy_engineering_results):
    """Test validator limits on airspeed sensors and GNSS redundancy counts."""
    m_result, c_result, w_result, a_result, t_result, f_result, p_result = dummy_engineering_results
    reqs = AvionicsRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result, propulsion_result=p_result
    )
    
    constraints = AvionicsConstraints(
        min_comms_range_km=10.0,
        required_gnss_count=2,
    )
    
    validator = AvionicsValidator()
    
    nav = NavigationAnalysis("Standard", 1, True, False, 20.0)  # low redundancy (1 < 2)
    comm = CommunicationAnalysis(15.0, 64.0, True, 5.0)
    pow_anal = PowerAnalysis(8.0, 10.0, False, 1.6)

    # Case 1: Low GNSS count violates redundancy
    with pytest.raises(AvionicsValidationError) as excinfo:
        validator.validate(reqs, constraints, "Pixhawk 6C", ["Holybro Digital Airspeed Sensor", "Matek CAN Compass"], "None", nav, comm, pow_anal)
    assert "redundancy level constraint" in str(excinfo.value)

    # Case 2: Missing Airspeed Sensor is critical safety failure
    nav.redundancy_level = 2  # fix redundancy
    with pytest.raises(AvionicsValidationError) as excinfo:
        validator.validate(reqs, constraints, "Pixhawk 6C", ["Matek CAN Compass"], "None", nav, comm, pow_anal)
    assert "Airspeed sensor" in str(excinfo.value)


def test_avionics_engine_flow(dummy_engineering_results):
    """Test full integration loop in AvionicsEngine."""
    m_result, c_result, w_result, a_result, t_result, f_result, p_result = dummy_engineering_results
    reqs = AvionicsRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result, propulsion_result=p_result
    )
    
    engine = AvionicsEngine()
    result = engine.process_avionics_design(reqs)
    
    assert isinstance(result, AvionicsEngineResult)
    assert "Holybro Pixhawk" in result.selected_flight_controller or "Cube Orange" in result.selected_flight_controller
    assert "Digital Airspeed Sensor" in result.selected_sensors[0]
    assert result.navigation_analysis.estimated_cpu_load_pct > 0.0
    assert result.communication_analysis.max_range_km > 0.0
    assert result.power_analysis.continuous_power_w > 0.0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
