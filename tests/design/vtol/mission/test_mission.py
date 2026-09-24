import pytest
from backend.design.vtol.mission import (
    MissionRequirements,
    VTOLMissionCategory,
    VTOLType,
    TakeoffMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
    HoverRequirements,
    TransitionRequirements,
    CruiseRequirements,
    MissionEngine,
    MissionValidator,
    MissionValidationError,
    VTOLMissionStrategyRegistry,
)


@pytest.fixture
def valid_vtol_mission_requirements():
    hover = HoverRequirements(
        hover_duration_min=5.0,
        hover_altitude_m=100.0,
        wind_limit_hover_kts=15.0,
        climb_rate_vertical_m_s=2.5,
        descent_rate_vertical_m_s=2.0,
    )
    transition = TransitionRequirements(
        transition_speed_kmh=65.0,
        transition_duration_s=15.0,
        transition_altitude_m=120.0,
        max_transition_pitch_deg=20.0,
    )
    cruise = CruiseRequirements(
        cruise_speed_kmh=110.0,
        cruise_altitude_m=150.0,
        cruise_range_km=40.0,
        cruise_endurance_min=30.0,
        wind_limit_cruise_kts=20.0,
    )
    return MissionRequirements(
        mission_category=VTOLMissionCategory.CARGO,
        vtol_type=VTOLType.LIFT_CRUISE,
        payload_kg=5.0,
        hover_reqs=hover,
        transition_reqs=transition,
        cruise_reqs=cruise,
        max_altitude_m=1000.0,
        environment=EnvironmentType.RURAL,
        takeoff_method=TakeoffMethod.VERTICAL,
        landing_method=LandingMethod.VERTICAL,
        wind_limit_max_kts=22.0,
        temperature_limit_min_c=-10.0,
        temperature_limit_max_c=40.0,
        rain_tolerance="Light",
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        safety_requirements="Dual GNSS and parachute backup",
        budget=15000.0,
    )


def test_vtol_mission_creation(valid_vtol_mission_requirements):
    """Verify that we can construct mission requirements and nested sub-requirements."""
    reqs = valid_vtol_mission_requirements
    assert reqs.mission_category == VTOLMissionCategory.CARGO
    assert reqs.vtol_type == VTOLType.LIFT_CRUISE
    assert reqs.payload_kg == 5.0
    assert reqs.hover_reqs.hover_duration_min == 5.0
    assert reqs.transition_reqs.transition_speed_kmh == 65.0
    assert reqs.cruise_reqs.cruise_range_km == 40.0


def test_vtol_mission_strategy_selection():
    """Verify registry returns correct strategy based on category."""
    strategy = VTOLMissionStrategyRegistry.get(VTOLMissionCategory.SURVEY)
    assert strategy.category == VTOLMissionCategory.SURVEY
    assert strategy.get_hover_priority() == 0.30
    assert strategy.get_cruise_priority() == 0.70

    # Test delivery maps to Cargo
    deliv_strategy = VTOLMissionStrategyRegistry.get(VTOLMissionCategory.DELIVERY)
    assert deliv_strategy.category == VTOLMissionCategory.CARGO


def test_vtol_validation_success(valid_vtol_mission_requirements):
    """Verify standard valid inputs pass validator without errors."""
    validator = MissionValidator()
    # Should not raise exception
    validator.validate(valid_vtol_mission_requirements)


def test_vtol_validation_failures(valid_vtol_mission_requirements):
    """Verify validator catches range inconsistencies and value limits."""
    validator = MissionValidator()

    # Case 1: Inconsistent range vs endurance/speed
    reqs = valid_vtol_mission_requirements
    reqs.cruise_reqs.cruise_range_km = 500.0  # Cruising at 110kmh for 30min is physically max ~55km range. 500km is impossible.
    with pytest.raises(MissionValidationError) as excinfo:
        validator.validate(reqs)
    assert "physically inconsistent" in str(excinfo.value)

    # Reset
    reqs.cruise_reqs.cruise_range_km = 40.0

    # Case 2: Negative hover time
    reqs.hover_reqs.hover_duration_min = -5.0
    with pytest.raises(MissionValidationError) as excinfo:
        validator.validate(reqs)
    assert "cannot be negative" in str(excinfo.value)

    # Reset
    reqs.hover_reqs.hover_duration_min = 5.0

    # Case 3: Transition speed exceeds cruise speed
    reqs.transition_reqs.transition_speed_kmh = 150.0  # Cruise is 110 kmh
    with pytest.raises(MissionValidationError) as excinfo:
        validator.validate(reqs)
    assert "must be less than cruise speed" in str(excinfo.value)


def test_vtol_mission_engine_flow(valid_vtol_mission_requirements):
    """Verify engine processes valid requirements and computes outputs correctly."""
    engine = MissionEngine()
    result = engine.process_mission(valid_vtol_mission_requirements)

    assert result is not None
    assert result.mission_profile.total_endurance_min == pytest.approx(35.25)  # 5 + 30 + 15/60
    assert result.mission_profile.total_energy_demand_kwh > 0.0

    # Check density calculation logic
    assert result.mission_profile.air_density_hover_kg_m3 < 1.225
    assert result.mission_profile.air_density_cruise_kg_m3 < result.mission_profile.air_density_hover_kg_m3

    # Check prioritizations
    assert result.mission_analysis.hover_priority == 0.60
    assert result.mission_analysis.cruise_priority == 0.40

    # Sized MTOW checks
    assert result.mission_analysis.estimated_mtow_kg == pytest.approx(15.62, abs=1e-2)  # 5.0 / 0.32

    # Check recommendations & warnings
    assert len(result.recommendations) > 0
    assert len(result.warnings) == 0
