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
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements, FuselageType
from backend.design.fixed_wing.fuselage.fuselage_profile import FuselageProfile
from backend.design.fixed_wing.fuselage.fuselage_constraints import FuselageConstraints
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.mounting_interfaces import MountingInterfaces
from backend.design.fixed_wing.fuselage.internal_layout import InternalLayout
from backend.design.fixed_wing.fuselage.component_placement import ComponentPlacementService, ComponentPlacement
from backend.design.fixed_wing.fuselage.fuselage_analysis import FuselageAnalysisService, FuselageAnalysis
from backend.design.fixed_wing.fuselage.fuselage_validator import FuselageValidator, FuselageValidationError
from backend.design.fixed_wing.fuselage.fuselage_registry import FuselageStrategyRegistry
from backend.design.fixed_wing.fuselage.fuselage_strategy import CargoFuselageStrategy
from backend.design.fixed_wing.fuselage.fuselage_sizer import FuselageSizer
from backend.design.fixed_wing.fuselage.fuselage_engine import FuselageEngine
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult as FuselageEngineResult


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
    
    return m_result, c_result, w_result, a_result, t_result


def test_fuselage_sizing(dummy_engineering_results):
    """Verify that fuselage sizer creates correct dimensions based on wingspan."""
    m_result, c_result, w_result, a_result, t_result = dummy_engineering_results
    reqs = FuselageRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result
    )
    
    sizer = FuselageSizer()
    geom = sizer.size_fuselage_envelope(
        requirements=reqs,
        fineness_ratio=6.0,
        clearance_margin=0.01,
        cross_section="Rectangular",
        fuselage_type=FuselageType.CONVENTIONAL,
    )
    
    # wingspan b = 2.0 -> length = 2.0 * 0.75 = 1.5
    assert geom.length_m == pytest.approx(1.5)
    assert geom.total_volume_m3 > 0.0
    assert geom.payload_bay_volume_m3 > 0.0
    assert geom.battery_bay_volume_m3 > 0.0


def test_component_placement():
    """Test longitudinal center of gravity balancing moments equations."""
    service = ComponentPlacementService()
    placement = service.place_components(
        fuselage_length=1.5,
        wing_x_location=0.5,
        wing_mac=0.22,
        payload_mass=2.0,
        battery_mass=1.2,
        propulsion_layout="Tractor",
    )
    
    assert placement.target_cg_x_m == pytest.approx(0.5 + 0.25 * 0.22)
    assert placement.calculated_cg_x_m > 0.0
    assert "Battery" in placement.component_locations
    assert placement.static_margin_pct >= 0.0


def test_fuselage_volumetric_analysis():
    """Verify packaging efficiency and fineness ratio drag scoring."""
    service = FuselageAnalysisService()
    analysis = service.analyze_fuselage(
        length=1.5,
        width=0.25,
        height=0.25,
        payload_vol=0.005,
        battery_vol=0.002,
        total_vol=0.04,
        tail_style="Conventional",
        fuselage_type="Conventional",
    )
    assert analysis.volume_utilization_ratio == 0.182
    assert analysis.aerodynamic_efficiency_score > 0.0
    assert analysis.component_accessibility_score > 0.0


def test_fuselage_strategy_selection():
    """Verify registry matches strategies."""
    strategy = FuselageStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoFuselageStrategy)
    assert strategy.name == "Cargo"


def test_fuselage_validation_rules(dummy_engineering_results):
    """Test fuselage width boundaries and configuration checks."""
    m_result, c_result, w_result, a_result, t_result = dummy_engineering_results
    reqs = FuselageRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result
    )
    
    constraints = FuselageConstraints(
        min_payload_volume_m3=0.001,
        min_battery_volume_m3=0.0002,
    )
    
    validator = FuselageValidator()
    
    geom = FuselageGeometry(
        length_m=1.5,
        width_m=0.30,  # exceeds wing root chord (0.25)
        height_m=0.25,
        nose_length_m=0.25,
        tail_cone_length_m=0.6,
        cross_section_type="Rectangular",
        wing_attachment_x_m=0.5,
        tail_attachment_x_m=1.4,
        payload_bay_length_m=0.3,
        payload_bay_width_m=0.2,
        payload_bay_height_m=0.2,
        payload_bay_volume_m3=0.005,
        battery_bay_length_m=0.2,
        battery_bay_width_m=0.2,
        battery_bay_height_m=0.15,
        battery_bay_volume_m3=0.002,
        avionics_bay_length_m=0.2,
        avionics_bay_width_m=0.2,
        avionics_bay_height_m=0.1,
        total_volume_m3=0.04,
    )
    
    interfaces = MountingInterfaces("", "", "", "", "", 0.0, 0.0, "")
    layout = InternalLayout(0, 0, 0, 0, 0, 0, 0, "", "", "duct", "")
    analysis = FuselageAnalysis(80, 80, 80, 80, 80, 80, 0.18, "")

    # Case 1: Width exceeds wing root chord (blockage)
    with pytest.raises(FuselageValidationError) as excinfo:
        validator.validate(reqs, constraints, geom, interfaces, layout, analysis)
    assert "exceeds wing root chord" in str(excinfo.value)


def test_fuselage_engine_flow(dummy_engineering_results):
    """Test full integration loop in FuselageEngine."""
    m_result, c_result, w_result, a_result, t_result = dummy_engineering_results
    reqs = FuselageRequirements(
        mission_result=m_result, configuration_result=c_result, wing_result=w_result, airfoil_result=a_result, tail_result=t_result
    )
    
    engine = FuselageEngine()
    result = engine.process_fuselage_design(reqs)
    
    assert isinstance(result, FuselageEngineResult)
    assert result.fuselage_geometry.length_m > 0.0
    assert result.component_placement.calculated_cg_x_m > 0.0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
