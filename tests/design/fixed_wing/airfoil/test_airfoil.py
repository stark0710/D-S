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
from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements, AirfoilType
from backend.design.fixed_wing.airfoil.airfoil_profile import AirfoilProfile
from backend.design.fixed_wing.airfoil.airfoil_constraints import AirfoilConstraints
from backend.design.fixed_wing.airfoil.airfoil_validator import AirfoilValidator, AirfoilValidationError
from backend.design.fixed_wing.airfoil.airfoil_database import AirfoilDatabase, AirfoilRecord
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysisService, ReynoldsAnalysis
from backend.design.fixed_wing.airfoil.polar_analysis import PolarAnalysisService, PolarData
from backend.design.fixed_wing.airfoil.performance_map import PerformanceMapService, PerformanceMap
from backend.design.fixed_wing.airfoil.airfoil_analysis import AirfoilAnalysisService
from backend.design.fixed_wing.airfoil.airfoil_registry import AirfoilStrategyRegistry
from backend.design.fixed_wing.airfoil.airfoil_strategy import CargoAirfoilStrategy
from backend.design.fixed_wing.airfoil.airfoil_engine import AirfoilEngine
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult as AirfoilEngineResult


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
    return m_result, c_result, w_result


def test_airfoil_db_lookup():
    """Verify that airfoil database holds standard airfoils and corrects Cl/Cd for Reynolds."""
    record = AirfoilDatabase.get_airfoil("Clark Y")
    assert record is not None
    assert record.name == "Clark Y"
    assert record.thickness_ratio == 0.117
    
    # Verify lift increases with Re
    cl_max_low = record.get_max_lift_coefficient(100000.0)
    cl_max_high = record.get_max_lift_coefficient(500000.0)
    assert cl_max_high > cl_max_low

    # Verify drag decreases with Re at constant Cl
    cd_low = record.get_drag_coefficient(0.4, 100000.0)
    cd_high = record.get_drag_coefficient(0.4, 500000.0)
    assert cd_high < cd_low


def test_reynolds_calculation():
    """Test Sutherland viscosity and Reynolds chord calculations."""
    service = ReynoldsAnalysisService()
    reynolds = service.analyze_reynolds_envelope(
        air_density=1.225,
        cruise_speed_m_s=22.2,
        stall_speed_m_s=12.5,
        root_chord_m=0.3,
        tip_chord_m=0.15,
        mac_m=0.23,
    )
    assert reynolds.re_root_cruise > reynolds.re_tip_cruise
    assert reynolds.re_root_cruise > reynolds.re_root_stall
    assert "re_root_cruise" in reynolds.__slots__


def test_polar_analysis():
    """Verify section lift-to-drag calculations."""
    airfoil = AirfoilDatabase.get_airfoil("Clark Y")
    service = PolarAnalysisService()
    polar = service.analyze_polar(airfoil, target_cl=0.45, reynolds=200000.0)
    
    assert polar.airfoil_name == "Clark Y"
    assert polar.cruise_cd > 0.0
    assert polar.cruise_l_d == pytest.approx(0.45 / polar.cruise_cd, rel=1e-2)
    assert polar.max_l_d >= polar.cruise_l_d
    assert "cl" in polar.polar_curve
    assert len(polar.polar_curve["cl"]) > 0


def test_performance_mapping():
    """Test 2D grid generation of Cd and L/D across Re and Cl."""
    airfoil = AirfoilDatabase.get_airfoil("Clark Y")
    service = PerformanceMapService()
    perf_map = service.generate_map(airfoil, reynolds_min=100000.0, reynolds_max=500000.0)
    
    assert perf_map.airfoil_name == "Clark Y"
    assert len(perf_map.reynolds_nodes) == 5
    assert len(perf_map.cl_nodes) == 6
    assert len(perf_map.drag_grid) == 5
    assert len(perf_map.drag_grid[0]) == 6


def test_strategy_selection():
    """Verify registry looks up matching strategies."""
    strategy = AirfoilStrategyRegistry.get("cargo")
    assert isinstance(strategy, CargoAirfoilStrategy)
    assert strategy.name == "Cargo"


def test_airfoil_validation(dummy_engineering_results):
    """Test validation rules (e.g. low-thickness limits, symmetrical roots, etc.)."""
    m_result, c_result, w_result = dummy_engineering_results
    reqs = AirfoilRequirements(mission_result=m_result, configuration_result=c_result, wing_result=w_result)
    
    constraints = AirfoilConstraints(
        max_pitching_moment_magnitude=0.10,
        min_thickness_to_chord=0.07,
    )
    
    validator = AirfoilValidator()
    
    # Sized flow
    reynolds = ReynoldsAnalysis(
        re_root_cruise=200000.0,
        re_tip_cruise=100000.0,
        re_mean_cruise=150000.0,
        re_root_stall=110000.0,
        re_tip_stall=55000.0,
        recommended_re_range="",
    )

    # Case 1: Incompatible Symmetrical root for Cargo
    m_result.mission_profile.mission_category = MissionCategory.CARGO
    root = AirfoilDatabase.get_airfoil("NACA 0012")  # Symmetrical
    tip = AirfoilDatabase.get_airfoil("Clark Y")
    with pytest.raises(AirfoilValidationError) as excinfo:
        validator.validate(reqs, constraints, root, tip, reynolds)
    assert "Symmetrical airfoil" in str(excinfo.value)

    # Case 2: Thin wing root on high AR structure is incompatible
    m_result.mission_profile.mission_category = MissionCategory.LONG_ENDURANCE
    w_result.wing_geometry.aspect_ratio = 15.0  # High AR
    root = AirfoilDatabase.get_airfoil("MH 32")    # Thin (8.7% < 9.0%)
    with pytest.raises(AirfoilValidationError) as excinfo:
        validator.validate(reqs, constraints, root, tip, reynolds)
    assert "is too thin for a high aspect ratio wing" in str(excinfo.value)


def test_airfoil_engine_flow(dummy_engineering_results):
    """Test full integration loop of AirfoilEngine."""
    m_result, c_result, w_result = dummy_engineering_results
    reqs = AirfoilRequirements(mission_result=m_result, configuration_result=c_result, wing_result=w_result)
    
    engine = AirfoilEngine()
    result = engine.process_airfoil_design(reqs)
    
    assert isinstance(result, AirfoilEngineResult)
    assert result.selected_root_airfoil in AirfoilDatabase.list_airfoils()
    assert result.selected_tip_airfoil in AirfoilDatabase.list_airfoils()
    assert result.polar_data.cruise_l_d > 0.0
    assert len(result.performance_map.drag_grid) > 0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
