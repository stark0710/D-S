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
from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements, PropulsionType, PropulsionLayout
from backend.design.fixed_wing.propulsion.propulsion_profile import PropulsionProfile
from backend.design.fixed_wing.propulsion.propulsion_constraints import PropulsionConstraints
from backend.design.fixed_wing.propulsion.motor_selector import MotorSelector
from backend.design.fixed_wing.propulsion.engine_selector import EngineSelector
from backend.design.fixed_wing.propulsion.propeller_selector import PropellerSelector
from backend.design.fixed_wing.propulsion.thrust_analysis import ThrustAnalysis
from backend.design.fixed_wing.propulsion.power_analysis import PowerAnalysis
from backend.design.fixed_wing.propulsion.efficiency_analysis import EfficiencyAnalysis
from backend.design.fixed_wing.propulsion.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.propulsion.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.propulsion.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.propulsion.propulsion_validator import PropulsionValidator, PropulsionValidationError
from backend.design.fixed_wing.propulsion.propulsion_registry import PropulsionStrategyRegistry
from backend.design.fixed_wing.propulsion.propulsion_strategy import CargoPropulsionStrategy
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult as PropulsionEngineResult


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
    
    return m_result, c_result, w_result, a_result, t_result, f_result


def test_motor_selection():
    """Verify that motor selector finds appropriate KV/weight models."""
    selector = MotorSelector()
    motor = selector.select_best_motor(target_power_w=500.0, mission_category="Balanced")
    assert motor.name == "SunnySky X2820"
    assert motor.max_power_w >= 500.0

    motor_heavy = selector.select_best_motor(target_power_w=2000.0, mission_category="Cargo")
    assert motor_heavy.name == "KDE Direct 7215XF"


def test_engine_selection():
    """Verify engine selection from gas displacement database."""
    selector = EngineSelector()
    engine = selector.select_best_engine(target_power_w=1600.0)
    # DLE 20cc has 2.5 HP (1864 W), but O.S. GT15 has 2.4 HP (1789 W) and is lighter (630g vs 820g)
    assert engine.name == "O.S. GT15"
    assert engine.max_power_w >= 1600.0


def test_propeller_selection():
    """Test actuator disk theory propeller diameter calculations."""
    selector = PropellerSelector()
    prop = selector.select_propeller(target_thrust_n=20.0, shaft_power_w=800.0, air_density=1.2, max_diameter_m=0.5)
    assert prop.diameter_m <= 0.5
    assert prop.diameter_in >= 9.0


def test_propulsion_strategy_selection():
    """Verify registry matches strategies."""
    strategy = PropulsionStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoPropulsionStrategy)
    assert strategy.name == "Cargo"


def test_propulsion_validation_rules(dummy_engineering_results):
    """Test validator limits on T/W, climb capabilities, and gas tail compatibilities."""
    m_result, c_result, w_result, a_result, t_result, f_result = dummy_engineering_results
    reqs = PropulsionRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result
    )
    
    constraints = PropulsionConstraints(min_thrust_to_weight=0.5)
    validator = PropulsionValidator()
    
    t_anal = ThrustAnalysis(10.0, 30.0, 25.0, 0.35, 150.0)  # low T/W
    p_anal = PowerAnalysis(200.0, 450.0, 600.0, 15.0)
    c_anal = CruiseAnalysis(80.0, 10.0, 5000.0, 50.0)
    cl_anal = ClimbAnalysis(3.0, 10.0, 200.0, 2.0)
    to_anal = TakeoffAnalysis(20.0, 12.0, 15.0, 4.0)

    # Case 1: T/W below constraints limits
    with pytest.raises(PropulsionValidationError) as excinfo:
        validator.validate(reqs, constraints, PropulsionType.ELECTRIC, t_anal, p_anal, c_anal, cl_anal, to_anal)
    assert "Takeoff thrust-to-weight ratio" in str(excinfo.value)

    # Case 2: ICE on Tailless layout is incompatible
    t_result.tail_configuration = "Tailless"
    t_anal.thrust_to_weight_ratio = 0.65  # fix T/W
    with pytest.raises(PropulsionValidationError) as excinfo:
        validator.validate(reqs, constraints, PropulsionType.ICE, t_anal, p_anal, c_anal, cl_anal, to_anal)
    assert "ICE" in str(excinfo.value) and "incompatible" in str(excinfo.value)


def test_propulsion_engine_flow(dummy_engineering_results):
    """Test full integration loop in PropulsionEngine."""
    m_result, c_result, w_result, a_result, t_result, f_result = dummy_engineering_results
    reqs = PropulsionRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result, fuselage_result=f_result
    )
    
    engine = PropulsionEngine()
    result = engine.process_propulsion_design(reqs)
    
    assert isinstance(result, PropulsionEngineResult)
    assert result.selected_motor_or_engine in ["SunnySky X2820", "SunnySky X2216", "T-Motor AT4120", "T-Motor AT3520", "T-Motor MN5008"]
    assert "x" in result.selected_propeller
    assert result.thrust_analysis.thrust_to_weight_ratio > 0.0
    assert result.climb_analysis.rate_of_climb_m_s > 0.0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
