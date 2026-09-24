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
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_profile import WingProfile
from backend.design.fixed_wing.wing.wing_constraints import WingConstraints
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_validator import WingValidator, WingValidationError
from backend.design.fixed_wing.wing.wing_registry import WingStrategyRegistry
from backend.design.fixed_wing.wing.wing_strategy import LongEnduranceWingStrategy
from backend.design.fixed_wing.wing.wing_planform import PlanformGeometryService
from backend.design.fixed_wing.wing.wing_sizer import WingSizer
from backend.design.fixed_wing.wing.wing_engine import WingEngine
from backend.design.fixed_wing.wing.wing_result import WingResult as WingEngineResult


@pytest.fixture
def dummy_mission_and_config():
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
    return m_result, c_result


def test_wing_sizing_calculation(dummy_mission_and_config):
    """Test core wing sizing equations."""
    m_result, c_result = dummy_mission_and_config
    reqs = WingRequirements(mission_result=m_result, configuration_result=c_result)
    
    constraints = WingConstraints(
        max_wingspan_m=3.0,
        min_aspect_ratio=4.0,
        max_aspect_ratio=20.0,
        min_wing_loading_kg_m2=2.0,
        max_wing_loading_kg_m2=50.0,
    )
    
    sizer = WingSizer()
    size_data = sizer.size_wing(reqs, constraints, target_aspect_ratio=10.0, typical_wing_loading_kg_m2=15.0)
    
    assert size_data["area_m2"] > 0.0
    assert size_data["aspect_ratio"] == pytest.approx(10.0)
    assert size_data["span_m"] > 0.0
    assert size_data["wing_loading_kg_m2"] > 0.0


def test_planform_geometry_generation():
    """Verify chords, MAC, and quarter-chord equations across different planforms."""
    service = PlanformGeometryService()
    
    # 1. Rectangular planform
    rect_data = service.calculate_planform_dimensions(
        planform=PlanformType.RECTANGULAR, area_m2=1.0, aspect_ratio=9.0, sweep_angle_deg=0.0
    )
    # b = sqrt(S * AR) = 3.0
    assert rect_data["span_m"] == pytest.approx(3.0)
    # root_chord = S / b = 1.0 / 3.0 = 0.3333
    assert rect_data["root_chord_m"] == 0.3333
    assert rect_data["taper_ratio"] == 1.0
    assert rect_data["mean_aerodynamic_chord_m"] == 0.3333
    assert rect_data["quarter_chord_x_m"] == round(0.25 * 0.3333, 4)

    # 2. Tapered planform
    taper_data = service.calculate_planform_dimensions(
        planform=PlanformType.TAPERED, area_m2=1.0, aspect_ratio=9.0, sweep_angle_deg=0.0
    )
    assert taper_data["taper_ratio"] == 0.5
    assert taper_data["root_chord_m"] > taper_data["tip_chord_m"]


def test_strategy_selection():
    """Verify wing strategy registry fetches concrete subclasses."""
    strategy = WingStrategyRegistry.get("long endurance")
    assert isinstance(strategy, LongEnduranceWingStrategy)
    assert strategy.name == "Long Endurance"


def test_wing_validation_rules(dummy_mission_and_config):
    """Test validation rules for aspect ratio, wing loading limits, and configuration compatibility."""
    m_result, c_result = dummy_mission_and_config
    reqs = WingRequirements(mission_result=m_result, configuration_result=c_result)

    constraints = WingConstraints(
        max_wingspan_m=3.0,
        min_aspect_ratio=4.0,
        max_aspect_ratio=15.0,
        min_wing_loading_kg_m2=5.0,
        max_wing_loading_kg_m2=40.0,
    )

    validator = WingValidator()

    # Case 1: Incompatible Twin Boom + Delta Wing
    reqs.preferred_planform = PlanformType.DELTA
    c_result.selected_configuration["tail_configuration"] = "Twin Boom"

    geometry = WingGeometry(
        span_m=2.0,
        area_m2=0.4,
        aspect_ratio=10.0,
        wing_loading_kg_m2=20.0,
        root_chord_m=0.25,
        tip_chord_m=0.15,
        taper_ratio=0.6,
        sweep_angle_deg=10.0,
        dihedral_angle_deg=2.0,
        wing_incidence_deg=2.0,
        mean_aerodynamic_chord_m=0.22,
        quarter_chord_x_m=0.1,
        reference_area_m2=0.4,
    )

    with pytest.raises(WingValidationError) as excinfo:
        validator.validate(reqs, constraints, geometry, {"is_feasible": True})
    assert "incompatible with Twin Boom tail layouts" in str(excinfo.value)


def test_wing_engine_flow(dummy_mission_and_config):
    """Verify full orchestration loop in WingEngine."""
    m_result, c_result = dummy_mission_and_config
    reqs = WingRequirements(mission_result=m_result, configuration_result=c_result)

    engine = WingEngine()
    result = engine.process_wing_design(reqs)

    assert isinstance(result, WingEngineResult)
    assert result.aspect_ratio > 0.0
    assert result.wing_geometry.span_m > 0.0
    assert result.analysis.estimated_stall_speed_kmh > 0.0
    assert len(result.recommendations) > 0
    assert len(result.warnings) == 0
