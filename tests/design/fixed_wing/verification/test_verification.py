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
from backend.design.fixed_wing.propulsion.climb_analysis import ClimbAnalysis as PropClimbAnalysis
from backend.design.fixed_wing.propulsion.takeoff_analysis import TakeoffAnalysis as PropTakeoffAnalysis
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult
from backend.design.fixed_wing.avionics.navigation_analysis import NavigationAnalysis
from backend.design.fixed_wing.avionics.communication_analysis import CommunicationAnalysis
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis as AvPowerAnalysis
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult
from backend.design.fixed_wing.payload.payload_layout import PayloadLayout
from backend.design.fixed_wing.payload.payload_mount import PayloadMount
from backend.design.fixed_wing.payload.payload_power import PayloadPowerInterface
from backend.design.fixed_wing.payload.payload_data import PayloadDataInterface
from backend.design.fixed_wing.payload.payload_cooling import PayloadCooling
from backend.design.fixed_wing.payload.payload_analysis import PayloadAnalysis as PayPayloadAnalysis
from backend.design.fixed_wing.payload.payload_result import PayloadResult
from backend.design.fixed_wing.mass_properties.weight_breakdown import WeightBreakdown
from backend.design.fixed_wing.mass_properties.component_mass import ComponentMass
from backend.design.fixed_wing.mass_properties.loading_conditions import LoadingCondition
from backend.design.fixed_wing.mass_properties.mass_analysis import MassAnalysis
from backend.design.fixed_wing.mass_properties.mass_result import MassResult
from backend.design.fixed_wing.flight_performance.aerodynamic_analysis import AerodynamicAnalysis
from backend.design.fixed_wing.flight_performance.performance_analysis import PerformanceAnalysis
from backend.design.fixed_wing.flight_performance.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.flight_performance.landing_analysis import LandingAnalysis
from backend.design.fixed_wing.flight_performance.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.flight_performance.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.flight_performance.descent_analysis import DescentAnalysis
from backend.design.fixed_wing.flight_performance.stall_analysis import StallAnalysis
from backend.design.fixed_wing.flight_performance.glide_analysis import GlideAnalysis
from backend.design.fixed_wing.flight_performance.turn_performance import TurnAnalysis
from backend.design.fixed_wing.flight_performance.range_analysis import RangeAnalysis
from backend.design.fixed_wing.flight_performance.endurance_analysis import EnduranceAnalysis
from backend.design.fixed_wing.flight_performance.ceiling_analysis import CeilingAnalysis
from backend.design.fixed_wing.flight_performance.stability_analysis import StabilityAnalysis
from backend.design.fixed_wing.flight_performance.mission_performance import MissionPerformance
from backend.design.fixed_wing.flight_performance.flight_result import FlightResult
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements
from backend.design.fixed_wing.verification.verification_profile import VerificationProfile
from backend.design.fixed_wing.verification.verification_constraints import VerificationConstraints
from backend.design.fixed_wing.verification.verification_registry import VerificationStrategyRegistry
from backend.design.fixed_wing.verification.verification_strategy import CargoVerificationStrategy
from backend.design.fixed_wing.verification.verification_validator import VerificationValidator, VerificationValidationError
from backend.design.fixed_wing.verification.verification_engine import VerificationEngine
from backend.design.fixed_wing.verification.verification_result import VerificationResult as VerificationEngineResult


@pytest.fixture
def dummy_engineering_results():
    profile = MissionProfile(
        mission_category=MissionCategory.SURVEY,
        payload_kg=2.0,
        flight_time_min=60.0,
        cruise_speed_kmh=95.0,
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
        target_cruise_speed_kmh=95.0,
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
        quarter_chord_x_m=0.55,
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
        quarter_chord_location=0.55,
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
    layout = InternalLayout(0, 0, 0.50, 0, 0, 0, 0, "", "", "duct", "")
    placement = ComponentPlacement(0.55, 0.55, 10.0, {}, {})
    interfaces = MountingInterfaces("", "", "", "", "", 0.0, 0.0, "")
    f_anal = FuselageAnalysis(80.0, 85.0, 90.0, 95.0, 80.0, 80.0, 0.18, "")
    fuse_res = FuselageResult(
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
    p_climb = PropClimbAnalysis(3.0, 10.0, 200.0, 2.0)
    p_takeoff = PropTakeoffAnalysis(20.0, 12.0, 15.0, 4.0)
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

    pay_layout = PayloadLayout(0.12, "Nadir Downward", 0.20, 0.15, 0.15, "Bottom hatch")
    pay_mount = PayloadMount("Rigid floor plate", "Grommets", 20.0, "4x M3 screws", 0.0)
    pay_power = PayloadPowerInterface(5.0, 3.0, "XT30", False, 15.0)
    pay_data = PayloadDataInterface("USB-C", 5.0, "CAMERA_FEEDBACK", 64.0)
    pay_cool = PayloadCooling(15.0, "Passive", 0.0, 60.0)
    pay_anal = PayPayloadAnalysis(90.0, 15.0, 5.0, 0.0, 0.0, 1.2, 3.0, "Moderate", 90.0, "Summary")
    pay_result = PayloadResult(
        selected_payloads=["Sony RX1R II (RGB)"],
        payload_layout=pay_layout,
        payload_mounts=[pay_mount],
        power_interfaces=[pay_power],
        communication_interfaces=[pay_data],
        cooling_requirements=pay_cool,
        payload_analysis=pay_anal,
    )

    mass_break = WeightBreakdown(2.0, 0.5, 0.3, 2.0, 3.5, 5.5, 0.22, 0.35)
    mass_anal = MassAnalysis(90.0, 95.0, 95.0, 3.0, 0.55, "Summary")
    mass_result = MassResult(
        weight_breakdown=mass_break,
        component_masses=[ComponentMass("Wing", 2.0, 0.55, 0.0, 0.0)],
        center_of_gravity=(0.576, 0.0, -0.02),
        moments_of_inertia=(0.2, 0.18, 0.35),
        loading_conditions=[],
        static_margin=0.18,
        mass_analysis=mass_anal,
    )

    aerodynamic = AerodynamicAnalysis(0.45, 0.028, 16.0, 0.023, 0.0039)
    perf_anal = PerformanceAnalysis(120.0, 95.0, 50.0, 16.0, 3.5)
    to = TakeoffAnalysis(25.0, 15.0, 3.0, 5.0)
    land = LandingAnalysis(30.0, 12.0, 2.5, 4.5)
    climb = ClimbAnalysis(3.5, 8.0, 15.0, 2.0)
    cruise = CruiseAnalysis(95.0, 15.0, 250.0, 55.0, 0.45)
    descent = DescentAnalysis(1.5, 4.0, 15.0)
    stall = StallAnalysis(56.9, 49.5, 14.0, "docile nose drop")
    glide = GlideAnalysis(16.0, 3.5, 1.2)
    turn = TurnAnalysis(45.0, 1.15, 30.0, 15.0)
    r_anal = RangeAnalysis(251.0, 213.0, 2.8)
    ed_anal = EnduranceAnalysis(188.0, 160.0, 223.0)
    ceiling = CeilingAnalysis(3200.0, 2900.0, 3200.0)
    stability = StabilityAnalysis(0.18, "Stable", "Stable", "Stable", 0.634)
    mission_perf = MissionPerformance(95.0, "Fully Compliant", 85.0)

    flight_res = FlightResult(
        aerodynamic_analysis=aerodynamic,
        performance_analysis=perf_anal,
        takeoff_analysis=to,
        landing_analysis=land,
        climb_analysis=climb,
        cruise_analysis=cruise,
        descent_analysis=descent,
        stall_analysis=stall,
        glide_analysis=glide,
        turn_analysis=turn,
        range_analysis=r_anal,
        endurance_analysis=ed_anal,
        ceiling_analysis=ceiling,
        stability_analysis=stability,
        mission_performance=mission_perf,
    )
    
    return m_result, c_result, w_result, a_result, t_result, fuse_res, p_result, av_result, pay_result, mass_result, flight_res


def test_verification_strategy_selection():
    """Verify strategy registry fetches correct verification strategies."""
    strategy = VerificationStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoVerificationStrategy)
    assert strategy.name == "Cargo"


def test_verification_validation_rules():
    """Test validator bounds for compliance scores and risk limits."""
    validator = VerificationValidator()

    # Case 1: Low compliance score fails verification validation
    with pytest.raises(VerificationValidationError) as excinfo:
        validator.validate(60.0, 85.0, 10.0, 30.0, [])
    assert "compliance score" in str(excinfo.value)

    # Case 2: High risk score fails verification validation
    with pytest.raises(VerificationValidationError) as excinfo:
        validator.validate(90.0, 85.0, 45.0, 30.0, [])
    assert "aircraft design risk index" in str(excinfo.value)


def test_verification_engine_flow(dummy_engineering_results):
    """Test full integration loop in VerificationEngine."""
    m_result, c_result, w_result, a_result, t_result, f_result, p_result, av_result, pay_result, mass_result, flight_res = dummy_engineering_results
    reqs = VerificationRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result, propulsion_result=p_result, avionics_result=av_result, payload_result=pay_result, mass_result=mass_result, flight_result=flight_res
    )

    engine = VerificationEngine()
    result = engine.process_verification(reqs)

    assert isinstance(result, VerificationEngineResult)
    assert result.compliance_report.compliance_score_pct > 80.0
    assert result.compliance_report.is_fully_compliant is True
    assert result.risk_analysis.overall_risk_score < 40.0
    assert result.verification_status == "VERIFIED"
    assert result.mission_status == "Ready"
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
