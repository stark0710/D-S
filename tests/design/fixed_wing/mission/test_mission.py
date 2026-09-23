import pytest
from backend.design.fixed_wing.mission.mission_requirements import (
    MissionRequirements,
    MissionCategory,
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
)
from backend.design.fixed_wing.mission.mission_validator import MissionValidator, MissionValidationError
from backend.design.fixed_wing.mission.mission_classifier import MissionClassifier
from backend.design.fixed_wing.mission.mission_scoring import MissionScoringService
from backend.design.fixed_wing.mission.mission_strategy import (
    SurveyMissionStrategy,
    LongEnduranceMissionStrategy,
    CargoMissionStrategy,
)
from backend.design.fixed_wing.mission.mission_engine import MissionEngine
from backend.design.fixed_wing.mission.mission_result import MissionResult


def test_mission_validation_valid():
    """Verify that a standard valid requirements payload passes validation."""
    reqs = MissionRequirements(
        mission_category=MissionCategory.SURVEY,
        payload_kg=1.5,
        flight_time_min=60.0,
        cruise_speed_kmh=75.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=8.0,
        operational_altitude_m=100.0,
        mission_range_km=30.0,
        launch_method=LaunchMethod.HAND_LAUNCH,
        landing_method=LandingMethod.BELLY_LANDING,
        budget=5000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    validator = MissionValidator()
    # Should not raise exception
    validator.validate(reqs)


def test_mission_validation_invalid_bounds():
    """Verify that negative bounds fail validation."""
    reqs = MissionRequirements(
        mission_category=MissionCategory.SURVEY,
        payload_kg=-0.5,  # negative
        flight_time_min=60.0,
        cruise_speed_kmh=75.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=8.0,
        operational_altitude_m=100.0,
        mission_range_km=30.0,
        launch_method=LaunchMethod.HAND_LAUNCH,
        landing_method=LandingMethod.BELLY_LANDING,
        budget=5000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    validator = MissionValidator()
    with pytest.raises(MissionValidationError) as excinfo:
        validator.validate(reqs)
    assert "Payload capacity must be positive" in str(excinfo.value)


def test_mission_validation_inconsistent_speeds():
    """Verify that stall speed exceeding cruise speed is blocked."""
    reqs = MissionRequirements(
        mission_category=MissionCategory.SURVEY,
        payload_kg=1.5,
        flight_time_min=60.0,
        cruise_speed_kmh=75.0,
        stall_speed_target_kmh=90.0,  # stall speed > cruise speed
        maximum_takeoff_weight_limit_kg=8.0,
        operational_altitude_m=100.0,
        mission_range_km=30.0,
        launch_method=LaunchMethod.HAND_LAUNCH,
        landing_method=LandingMethod.BELLY_LANDING,
        budget=5000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    validator = MissionValidator()
    with pytest.raises(MissionValidationError) as excinfo:
        validator.validate(reqs)
    assert "must be less than cruise speed" in str(excinfo.value)


def test_mission_validation_unfeasible_range():
    """Verify that range exceeding cruise speed and duration physics is blocked."""
    reqs = MissionRequirements(
        mission_category=MissionCategory.SURVEY,
        payload_kg=1.5,
        flight_time_min=60.0,
        cruise_speed_kmh=70.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=8.0,
        operational_altitude_m=100.0,
        mission_range_km=200.0,  # Speed is 70km/h, time is 60m. Range cannot be 200km!
        launch_method=LaunchMethod.HAND_LAUNCH,
        landing_method=LandingMethod.BELLY_LANDING,
        budget=5000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    validator = MissionValidator()
    with pytest.raises(MissionValidationError) as excinfo:
        validator.validate(reqs)
    assert "physically inconsistent" in str(excinfo.value)


def test_mission_validation_heavy_hand_launch():
    """Verify hand launching heavy weight is unsafe and blocked."""
    reqs = MissionRequirements(
        mission_category=MissionCategory.SURVEY,
        payload_kg=15.0,  # Heavy
        flight_time_min=60.0,
        cruise_speed_kmh=80.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=35.0,
        operational_altitude_m=100.0,
        mission_range_km=30.0,
        launch_method=LaunchMethod.HAND_LAUNCH,  # Unsafe for 15kg
        landing_method=LandingMethod.BELLY_LANDING,
        budget=5000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    validator = MissionValidator()
    with pytest.raises(MissionValidationError) as excinfo:
        validator.validate(reqs)
    assert "Hand Launch is unsafe" in str(excinfo.value)


def test_mission_classification():
    """Test classification rules for different requirements profiles."""
    classifier = MissionClassifier()

    # Case 1: Custom category gets inferred based on rules
    reqs = MissionRequirements(
        mission_category=MissionCategory.CUSTOM,
        payload_kg=12.0,  # Heavy -> Cargo
        flight_time_min=60.0,
        cruise_speed_kmh=80.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=40.0,
        operational_altitude_m=100.0,
        mission_range_km=30.0,
        launch_method=LaunchMethod.CATAPULT,
        landing_method=LandingMethod.PARACHUTE,
        budget=5000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )
    assert classifier.classify(reqs) == MissionCategory.CARGO

    # Case 2: Long endurance inference
    reqs.payload_kg = 1.0
    reqs.flight_time_min = 200.0  # > 180 min -> Long Endurance
    assert classifier.classify(reqs) == MissionCategory.LONG_ENDURANCE

    # Case 3: Preserve explicit categories
    reqs.mission_category = MissionCategory.TRAINING
    assert classifier.classify(reqs) == MissionCategory.TRAINING


def test_mission_scoring():
    """Verify complexity, feasibility, and normalizations score math."""
    scoring = MissionScoringService()

    reqs = MissionRequirements(
        mission_category=MissionCategory.SURVEY,
        payload_kg=2.0,
        flight_time_min=45.0,
        cruise_speed_kmh=60.0,
        stall_speed_target_kmh=35.0,
        maximum_takeoff_weight_limit_kg=8.0,
        operational_altitude_m=150.0,
        mission_range_km=20.0,
        launch_method=LaunchMethod.HAND_LAUNCH,
        landing_method=LandingMethod.BELLY_LANDING,
        budget=4000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.SEMI_AUTONOMOUS,
    )

    comp_score, comp_cat = scoring.calculate_complexity(reqs)
    assert comp_score > 0.0
    assert comp_cat in ("Low", "Medium", "High", "Very High")

    feasibility, warnings = scoring.calculate_feasibility(reqs)
    assert 0.0 <= feasibility <= 100.0

    m_score = scoring.calculate_mission_score(feasibility, comp_score)
    assert m_score > 0.0

    normalized = scoring.normalize_requirements(reqs)
    assert normalized["payload_mass_kg"] == 2.0
    assert normalized["cruise_speed_m_s"] == pytest.approx(60.0 / 3.6)
    assert normalized["flight_time_sec"] == 45.0 * 60.0


def test_mission_strategies():
    """Verify that strategies provide correct constants and recommendations."""
    survey = SurveyMissionStrategy()
    assert survey.get_target_payload_fraction() == 0.20
    assert survey.get_lift_to_drag_ratio() == 14.0
    assert len(survey.get_recommendations(None, None)) > 0

    endurance = LongEnduranceMissionStrategy()
    assert endurance.get_target_payload_fraction() == 0.15
    assert endurance.get_lift_to_drag_ratio() == 18.0


def test_mission_engine_flow():
    """Test full integration loop of MissionEngine."""
    engine = MissionEngine()
    reqs = MissionRequirements(
        mission_category=MissionCategory.SURVEY,
        payload_kg=1.5,
        flight_time_min=60.0,
        cruise_speed_kmh=75.0,
        stall_speed_target_kmh=45.0,
        maximum_takeoff_weight_limit_kg=8.0,
        operational_altitude_m=100.0,
        mission_range_km=30.0,
        launch_method=LaunchMethod.HAND_LAUNCH,
        landing_method=LandingMethod.BELLY_LANDING,
        budget=5000.0,
        environment=EnvironmentType.RURAL,
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
    )

    result = engine.process_mission(reqs)
    assert isinstance(result, MissionResult)
    assert result.mission_category == MissionCategory.SURVEY
    assert result.mission_score > 0.0
    assert result.mission_profile.energy_demand_kwh > 0.0
    assert len(result.recommendations) > 0
    assert "engine_version" in result.metadata
