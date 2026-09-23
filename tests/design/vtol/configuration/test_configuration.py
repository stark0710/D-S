import pytest
from backend.design.vtol.mission import (
    MissionResult,
    MissionProfile,
    HoverRequirements,
    TransitionRequirements,
    CruiseRequirements,
    MissionAnalysis,
    VTOLMissionCategory,
    VTOLType,
    TakeoffMethod,
    LandingMethod,
)
from backend.design.vtol.configuration import (
    ConfigurationRequirements,
    ConfigurationEngine,
    ConfigurationValidator,
    ConfigurationValidationError,
    VTOLConfigurationStrategyRegistry,
)


@pytest.fixture
def dummy_mission_result():
    hover = HoverRequirements(
        hover_duration_min=5.0,
        hover_altitude_m=100.0,
        wind_limit_hover_kts=12.0,
        climb_rate_vertical_m_s=2.5,
        descent_rate_vertical_m_s=2.0,
        metadata={"takeoff_method": TakeoffMethod.VERTICAL, "landing_method": LandingMethod.VERTICAL},
    )
    transition = TransitionRequirements(
        transition_speed_kmh=60.0,
        transition_duration_s=15.0,
        transition_altitude_m=120.0,
        max_transition_pitch_deg=20.0,
    )
    cruise = CruiseRequirements(
        cruise_speed_kmh=100.0,
        cruise_altitude_m=150.0,
        cruise_range_km=30.0,
        cruise_endurance_min=20.0,
        wind_limit_cruise_kts=18.0,
    )
    profile = MissionProfile(
        mission_category=VTOLMissionCategory.CARGO,
        vtol_type=VTOLType.LIFT_CRUISE,
        payload_kg=10.0,
        total_endurance_min=25.25,
        total_range_km=30.0,
        air_density_hover_kg_m3=1.21,
        air_density_cruise_kg_m3=1.20,
        energy_demand_hover_kwh=0.5,
        energy_demand_cruise_kwh=1.2,
        energy_demand_transition_kwh=0.1,
        total_energy_demand_kwh=1.8,
        complexity_score=0.55,
        complexity_category="Medium",
    )
    analysis = MissionAnalysis(
        hover_priority=0.6,
        cruise_priority=0.4,
        transition_complexity=0.5,
        estimated_mtow_kg=31.25,  # 10.0 / 0.32
        lift_to_drag_ratio_est=10.0,
        hover_thrust_to_weight_est=1.45,
        mission_energy_demand_kwh=1.8,
        mission_risk_score=0.4,
        mission_feasibility_score=85.0,
    )
    return MissionResult(
        mission_profile=profile,
        hover_requirements=hover,
        transition_requirements=transition,
        cruise_requirements=cruise,
        mission_analysis=analysis,
        engineering_notes=["Standard Sized Cargo profile."],
        recommendations=["Design clean fuselage cargo pods."],
        warnings=[],
        metadata={},
    )


def test_configuration_strategy_selection():
    """Verify registry returns configuration strategies based on category."""
    strategy = VTOLConfigurationStrategyRegistry.get(VTOLMissionCategory.LONG_ENDURANCE)
    assert strategy is not None
    assert strategy.category == VTOLMissionCategory.LONG_ENDURANCE
    assert strategy.score_vtol_type(VTOLType.TILT_ROTOR) == 95.0


def test_configuration_validation_failures(dummy_mission_result):
    """Verify validator flags invalid motor count and mismatching parameters."""
    validator = ConfigurationValidator()

    # Case 1: Negative motor count
    reqs = ConfigurationRequirements(
        mission_result=dummy_mission_result,
        desired_motor_count=-4,
    )
    with pytest.raises(ConfigurationValidationError) as excinfo:
        validator.validate(reqs)
    assert "must be positive" in str(excinfo.value)

    # Case 2: Excessive motor count
    reqs.desired_motor_count = 45
    with pytest.raises(ConfigurationValidationError) as excinfo:
        validator.validate(reqs)
    assert "exceeds mechanical complexity limit" in str(excinfo.value)

    # Case 3: Redundancy check mismatch
    reqs.desired_motor_count = 4
    reqs.redundancy_requirement = "Single Motor Out"
    with pytest.raises(ConfigurationValidationError) as excinfo:
        validator.validate(reqs)
    assert "requires at least 6 motors" in str(excinfo.value)


def test_configuration_engine_design_flow(dummy_mission_result):
    """Verify configuration engine generates correct spatial coordinates, modes, and trade-offs."""
    engine = ConfigurationEngine()
    reqs = ConfigurationRequirements(
        mission_result=dummy_mission_result,
        preferred_vtol_type=None,
    )
    result = engine.design_configuration(reqs)

    # selected configuration check
    assert result.selected_configuration == VTOLType.LIFT_CRUISE  # CARGO defaults to LIFT_CRUISE

    # flight modes check
    assert result.flight_mode_configuration is not None
    assert len(result.flight_mode_configuration.get_all_modes()) == 8
    assert result.flight_mode_configuration.hover.is_active is True
    assert result.flight_mode_configuration.cruise.attitude_control == "Aerodynamic surfaces"

    # lift and propulsion layouts check
    assert result.lift_architecture.motor_count == 4
    assert result.forward_propulsion_layout.motor_count == 1

    # actuator placements geometry checks (symmetry and size)
    assert result.actuator_layout.control_channels_count == 9  # 5 ESCs + 4 servos
    placements = result.actuator_layout.actuator_placements
    assert len(placements) > 0

    # check left/right symmetry for y coordinates
    ailerons = [p for p in placements if "Aileron" in p["name"]]
    assert len(ailerons) == 2
    y_coords = [p["y_m"] for p in ailerons]
    assert abs(y_coords[0] + y_coords[1]) == pytest.approx(0.0)  # should sum to 0 due to +/- y

    # trade-off analysis checks
    assert result.configuration_analysis.hover_efficiency == 85.0
    assert result.configuration_analysis.cruise_efficiency == 70.0
    assert result.configuration_analysis.mission_suitability == 95.0

    # warning check (control channels count is 9 <= 16, so no warning)
    assert len(result.warnings) == 0
