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
from backend.design.fixed_wing.payload.payload_layout import PayloadLayout
from backend.design.fixed_wing.payload.payload_mount import PayloadMount
from backend.design.fixed_wing.payload.payload_power import PayloadPowerInterface
from backend.design.fixed_wing.payload.payload_data import PayloadDataInterface
from backend.design.fixed_wing.payload.payload_cooling import PayloadCooling
from backend.design.fixed_wing.payload.payload_analysis import PayloadAnalysis
from backend.design.fixed_wing.payload.payload_result import PayloadResult
from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
from backend.design.fixed_wing.mass_properties.mass_profile import MassProfile
from backend.design.fixed_wing.mass_properties.mass_constraints import MassConstraints
from backend.design.fixed_wing.mass_properties.component_mass import ComponentMass
from backend.design.fixed_wing.mass_properties.cg_calculator import CGCalculator
from backend.design.fixed_wing.mass_properties.inertia_calculator import InertiaCalculator
from backend.design.fixed_wing.mass_properties.loading_conditions import LoadingCondition
from backend.design.fixed_wing.mass_properties.stability_margin import StabilityMarginCalculator
from backend.design.fixed_wing.mass_properties.weight_breakdown import WeightBreakdown
from backend.design.fixed_wing.mass_properties.mass_analysis import MassAnalysis as EngineMassAnalysis
from backend.design.fixed_wing.mass_properties.mass_validator import MassValidator, MassValidationError
from backend.design.fixed_wing.mass_properties.mass_registry import MassStrategyRegistry
from backend.design.fixed_wing.mass_properties.mass_strategy import CargoMassStrategy
from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.fixed_wing.mass_properties.mass_result import MassResult as MassEngineResult


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

    pay_layout = PayloadLayout(0.12, "Nadir Downward", 0.20, 0.15, 0.15, "Bottom hatch")
    pay_mount = PayloadMount("Rigid floor plate", "Grommets", 20.0, "4x M3 screws", 0.0)
    pay_power = PayloadPowerInterface(5.0, 3.0, "XT30", False, 15.0)
    pay_data = PayloadDataInterface("USB-C", 5.0, "CAMERA_FEEDBACK", 64.0)
    pay_cool = PayloadCooling(15.0, "Passive", 0.0, 60.0)
    pay_anal = PayloadAnalysis(90.0, 15.0, 5.0, 0.0, 0.0, 1.2, 3.0, "Moderate", 90.0, "Summary")
    pay_result = PayloadResult(
        selected_payloads=["Sony RX1R II (RGB)"],
        payload_layout=pay_layout,
        payload_mounts=[pay_mount],
        power_interfaces=[pay_power],
        communication_interfaces=[pay_data],
        cooling_requirements=pay_cool,
        payload_analysis=pay_anal,
    )
    
    return m_result, c_result, w_result, a_result, t_result, f_result, p_result, av_result, pay_result


def test_cg_calculation():
    """Verify CG calculation on simple structures."""
    calc = CGCalculator()
    components = [
        ComponentMass("Nose Motor", 1.0, 0.0, 0.0, 0.0),
        ComponentMass("Tail Boom", 1.0, 1.0, 0.0, 0.0),
    ]
    x, y, z = calc.calculate_cg(components)
    # CG should be exactly at 0.5m
    assert x == 0.5
    assert y == 0.0
    assert z == 0.0


def test_inertia_calculation():
    """Verify Parallel Axis Theorem calculation on point masses."""
    calc = InertiaCalculator()
    components = [
        ComponentMass("Wing Tip Left", 1.0, 0.5, -1.0, 0.0),
        ComponentMass("Wing Tip Right", 1.0, 0.5, 1.0, 0.0),
    ]
    # CG is at (0.5, 0.0, 0.0)
    ixx, iyy, izz = calc.calculate_moments_of_inertia(components, 0.5, 0.0, 0.0)
    
    # Ixx = sum m * (y^2 + z^2) = 1.0 * (-1.0^2) + 1.0 * (1.0^2) = 2.0 kg*m^2
    assert ixx == 2.0
    # Iyy = sum m * (x^2 + z^2) = 1.0 * (0.0^2) + 1.0 * (0.0^2) = 0.0
    assert iyy == 0.0
    # Izz = sum m * (x^2 + y^2) = 1.0 * (0.0^2 + -1.0^2) + 1.0 * (0.0^2 + 1.0^2) = 2.0
    assert izz == 2.0


def test_stability_margin_estimation():
    """Verify static margins for tailless and conventional layouts."""
    calc = StabilityMarginCalculator()
    wing_geom = WingGeometry(2.0, 0.4, 10.0, 20.0, 0.25, 0.15, 0.6, 0.0, 2.0, 2.0, 0.20, 0.08, 0.4)

    # Conventional: NP around 42% of MAC. MAC is 0.20. quarter_chord is 0.08.
    # NP = 0.08 + 0.42 * 0.20 = 0.164m.
    # CG at 0.124m. Margin = (0.164 - 0.124) / 0.20 = 0.04m / 0.20 = 20% (0.20)
    conventional_tail = TailResult("Conventional", None, None, None, {}, None)
    sm = calc.calculate_static_margin(0.124, wing_geom, conventional_tail)
    assert abs(sm - 0.20) < 1e-4

    # Tailless: NP around 25% of MAC.
    # NP = 0.08 + 0.25 * 0.20 = 0.13m.
    # CG at 0.11m. Margin = (0.13 - 0.11) / 0.20 = 10% (0.10)
    tailless_tail = TailResult("Tailless", None, None, None, {}, None)
    sm_tailless = calc.calculate_static_margin(0.11, wing_geom, tailless_tail)
    assert abs(sm_tailless - 0.10) < 1e-4


def test_mass_strategy_selection():
    """Verify Strategy Registry fetches correct strategies."""
    strategy = MassStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoMassStrategy)
    assert strategy.name == "Cargo"


def test_mass_validation_rules(dummy_engineering_results):
    """Test validator bounds for MTOW limits and dangerous stability margins."""
    m_result, c_result, w_result, a_result, t_result, f_result, p_result, av_result, pay_result = dummy_engineering_results
    reqs = MassRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result, propulsion_result=p_result, avionics_result=av_result, payload_result=pay_result
    )

    constraints = MassConstraints(max_takeoff_weight_kg=10.0, min_static_margin=0.08)
    profile = MassProfile()
    validator = MassValidator()

    lc = LoadingCondition("Operational Empty", 5.0, 0.12, 0.0, 0.0, 0.12)

    # Case 1: MTOW exceeds limits
    with pytest.raises(MassValidationError) as excinfo:
        validator.validate(reqs, constraints, profile, 12.0, 0.12, 0.15, [lc])
    assert "takeoff weight" in str(excinfo.value)

    # Case 2: Instability (Low Static Margin)
    with pytest.raises(MassValidationError) as excinfo:
        validator.validate(reqs, constraints, profile, 8.0, 0.12, 0.05, [lc])
    assert "static stability margin" in str(excinfo.value)


def test_mass_properties_engine_flow(dummy_engineering_results):
    """Test full integration loop in MassPropertiesEngine."""
    m_result, c_result, w_result, a_result, t_result, f_result, p_result, av_result, pay_result = dummy_engineering_results
    reqs = MassRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result, propulsion_result=p_result, avionics_result=av_result, payload_result=pay_result
    )

    engine = MassPropertiesEngine()
    result = engine.process_mass_design(reqs)

    assert isinstance(result, MassEngineResult)
    assert len(result.component_masses) > 0
    assert result.center_of_gravity[0] > 0.0
    assert result.moments_of_inertia[1] > 0.0
    assert result.static_margin > 0.0
    assert len(result.loading_conditions) > 0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
