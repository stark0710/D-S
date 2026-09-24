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
from backend.design.fixed_wing.configuration.configuration_requirements import (
    ConfigurationRequirements,
    WingPosition,
    PropulsionLayout,
    TailConfiguration,
    LandingGearConfiguration,
)
from backend.design.fixed_wing.configuration.configuration_profile import ConfigurationProfile
from backend.design.fixed_wing.configuration.configuration_validator import (
    ConfigurationValidator,
    ConfigurationValidationError,
)
from backend.design.fixed_wing.configuration.configuration_scoring import ConfigurationScoringService
from backend.design.fixed_wing.configuration.configuration_registry import ConfigurationStrategyRegistry
from backend.design.fixed_wing.configuration.configuration_strategy import LongEnduranceConfigurationStrategy
from backend.design.fixed_wing.configuration.configuration_engine import ConfigurationEngine
from backend.design.fixed_wing.configuration.configuration_result import ConfigurationResult as ConfigResult


@pytest.fixture
def dummy_mission_result():
    # Helper to construct a valid MissionResult
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
    return MissionResult(
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


def test_configuration_validation_errors(dummy_mission_result):
    """Verify that inconsistent layout combinations fail validation."""
    validator = ConfigurationValidator()

    # Case 1: Low Wing + Belly Landing is incompatible
    reqs = ConfigurationRequirements(mission_result=dummy_mission_result)
    dummy_mission_result.mission_profile.landing_method = LandingMethod.BELLY_LANDING
    layout_incompatible = {
        "wing_position": WingPosition.LOW_WING.value,
        "propulsion_layout": PropulsionLayout.TRACTOR.value,
        "tail_configuration": TailConfiguration.CONVENTIONAL.value,
        "landing_gear_configuration": LandingGearConfiguration.BELLY_LANDING.value,
    }

    with pytest.raises(ConfigurationValidationError) as excinfo:
        validator.validate(reqs, layout_incompatible)
    assert "Low Wing configuration is incompatible with Belly Landing" in str(excinfo.value)

    # Case 2: Belly Landing gear vs Runway landing is incompatible
    dummy_mission_result.mission_profile.landing_method = LandingMethod.RUNWAY
    layout_gear_incompatible = {
        "wing_position": WingPosition.HIGH_WING.value,
        "propulsion_layout": PropulsionLayout.TRACTOR.value,
        "tail_configuration": TailConfiguration.CONVENTIONAL.value,
        "landing_gear_configuration": LandingGearConfiguration.BELLY_LANDING.value,
    }
    with pytest.raises(ConfigurationValidationError) as excinfo:
        validator.validate(reqs, layout_gear_incompatible)
    assert "incompatible with Runway landing" in str(excinfo.value)


def test_configuration_scoring(dummy_mission_result):
    """Test configuration layout score calculators."""
    scoring = ConfigurationScoringService()
    reqs = ConfigurationRequirements(mission_result=dummy_mission_result)
    layout = {
        "wing_position": WingPosition.HIGH_WING.value,
        "propulsion_layout": PropulsionLayout.TRACTOR.value,
        "tail_configuration": TailConfiguration.CONVENTIONAL.value,
        "landing_gear_configuration": LandingGearConfiguration.TRICYCLE.value,
    }

    scores = scoring.score_configuration(reqs, layout)
    assert scores["overall_score"] > 0.0
    assert scores["stability"] > 50.0
    assert scores["simplicity"] > 50.0


def test_strategy_registry():
    """Verify registry looks up matching configuration strategies."""
    strategy = ConfigurationStrategyRegistry.get("long endurance")
    assert isinstance(strategy, LongEnduranceConfigurationStrategy)
    assert strategy.name == "Long Endurance"


def test_configuration_engine_orchestration(dummy_mission_result):
    """Test full ConfigurationEngine loop."""
    engine = ConfigurationEngine()
    reqs = ConfigurationRequirements(mission_result=dummy_mission_result)
    
    result = engine.process_configuration(reqs)
    
    assert isinstance(result, ConfigResult)
    assert result.configuration_score > 0.0
    assert len(result.alternative_configurations) > 0
    assert result.wing_configuration in [w.value for w in WingPosition]
    assert result.propulsion_configuration in [p.value for p in PropulsionLayout]
    
    # Check that alternatives are ranked in descending order of score
    scores = [alt["score"] for alt in result.alternative_configurations]
    assert scores == sorted(scores, reverse=True)
