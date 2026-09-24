import pytest
import math
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
from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
from backend.design.fixed_wing.flight_performance.flight_profile import FlightProfile
from backend.design.fixed_wing.flight_performance.flight_performance_engine import FlightPerformanceEngine

@pytest.fixture
def concrete_flight_requirements():
    profile = MissionProfile(
        mission_category=MissionCategory.SURVEY,
        payload_kg=2.0,
        flight_time_min=60.0,
        cruise_speed_kmh=95.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=10.0,
        operational_altitude_m=150.0,
        mission_range_km=15.0,
        launch_method=LaunchMethod.RUNWAY,
        landing_method=LandingMethod.RUNWAY,
        budget=10000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        air_density_kg_m3=1.225,
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

    pay_layout = PayloadLayout(0.535, "Nadir Downward", 0.20, 0.15, 0.15, "Bottom hatch")
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

    # MTOW = 8 kg
    mass_break = WeightBreakdown(3.0, 0.8, 0.2, 2.0, 2.0, 4.0, 0.25, 0.25)
    mass_anal = MassAnalysis(90.0, 95.0, 95.0, 3.0, 0.55, "Summary")
    mass_result = MassResult(
        weight_breakdown=mass_break,
        component_masses=[ComponentMass("Wing", 3.0, 0.55, 0.0, 0.0)],
        center_of_gravity=(0.576, 0.0, -0.02),
        moments_of_inertia=(0.2, 0.18, 0.35),
        loading_conditions=[],
        static_margin=0.18,
        mass_analysis=mass_anal,
    )
    
    reqs = FlightRequirements(
        mission_result=m_result,
        configuration_result=c_result,
        wing_result=w_result,
        airfoil_result=a_result,
        tail_result=t_result,
        fuselage_result=f_result,
        propulsion_result=p_result,
        avionics_result=av_result,
        payload_result=pay_result,
        mass_result=mass_result,
    )
    return reqs

def test_takeoff_monotonic_behavior(concrete_flight_requirements):
    """Verify higher thrust-to-weight, lower wing loading, or higher density shortens takeoff roll."""
    engine = FlightPerformanceEngine()
    profile = FlightProfile(ground_friction_coefficient=0.4)
    
    # Baseline
    res_base = engine.process_performance_design(concrete_flight_requirements, profile=profile)
    dist_base = res_base.takeoff_analysis.takeoff_distance_m
    
    # 1. Higher Thrust-to-Weight (T/W) -> shorter takeoff distance
    concrete_flight_requirements.propulsion_result.thrust_analysis.thrust_to_weight_ratio = 0.8
    res_high_tw = engine.process_performance_design(concrete_flight_requirements, profile=profile)
    dist_high_tw = res_high_tw.takeoff_analysis.takeoff_distance_m
    assert dist_high_tw < dist_base
    
    # Restore T/W
    concrete_flight_requirements.propulsion_result.thrust_analysis.thrust_to_weight_ratio = 0.5
    
    # 2. Higher Wing Loading -> longer takeoff distance
    concrete_flight_requirements.wing_result.wing_geometry.wing_loading_kg_m2 = 30.0
    res_high_wl = engine.process_performance_design(concrete_flight_requirements, profile=profile)
    dist_high_wl = res_high_wl.takeoff_analysis.takeoff_distance_m
    assert dist_high_wl > dist_base
    
    # Restore Wing Loading
    concrete_flight_requirements.wing_result.wing_geometry.wing_loading_kg_m2 = 20.0
    
    # 3. Lower Density (Higher Altitude) -> longer takeoff distance
    concrete_flight_requirements.mission_result.mission_profile.operational_altitude_m = 2000.0
    res_high_alt = engine.process_performance_design(concrete_flight_requirements, profile=profile)
    dist_high_alt = res_high_alt.takeoff_analysis.takeoff_distance_m
    assert dist_high_alt > dist_base

def test_landing_monotonic_behavior(concrete_flight_requirements):
    """Verify higher wing loading, lower braking coefficient, or lower cl_max increases landing roll."""
    engine = FlightPerformanceEngine()
    profile_base = FlightProfile(braking_coefficient=0.4)
    
    # Baseline
    res_base = engine.process_performance_design(concrete_flight_requirements, profile=profile_base)
    dist_base = res_base.landing_analysis.landing_distance_m
    
    # 1. Higher Wing Loading -> longer landing distance
    concrete_flight_requirements.wing_result.wing_geometry.wing_loading_kg_m2 = 30.0
    res_high_wl = engine.process_performance_design(concrete_flight_requirements, profile=profile_base)
    dist_high_wl = res_high_wl.landing_analysis.landing_distance_m
    assert dist_high_wl > dist_base
    
    # Restore Wing Loading
    concrete_flight_requirements.wing_result.wing_geometry.wing_loading_kg_m2 = 20.0
    
    # 2. Lower Braking Coefficient (friction) -> longer landing distance
    profile_low_mu = FlightProfile(braking_coefficient=0.2)
    res_low_mu = engine.process_performance_design(concrete_flight_requirements, profile=profile_low_mu)
    dist_low_mu = res_low_mu.landing_analysis.landing_distance_m
    assert dist_low_mu > dist_base
    
    # 3. Higher CLmax -> shorter landing distance
    concrete_flight_requirements.airfoil_result.polar_data.max_lift_coeff = 1.8
    res_high_cl = engine.process_performance_design(concrete_flight_requirements, profile=profile_base)
    dist_high_cl = res_high_cl.landing_analysis.landing_distance_m
    assert dist_high_cl < dist_base
