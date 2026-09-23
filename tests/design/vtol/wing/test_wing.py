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
)
from backend.design.vtol.configuration import (
    ConfigurationResult,
    PropulsionLayout,
    FlightModeConfiguration,
    FlightMode,
    ActuatorLayout,
    ConfigurationAnalysis,
)
from backend.design.vtol.wing import (
    WingRequirements,
    WingEngine,
    WingValidator,
    WingValidationError,
    VTOLWingStrategyRegistry,
)


@pytest.fixture
def dummy_mission_result():
    hover = HoverRequirements(
        hover_duration_min=5.0,
        hover_altitude_m=100.0,
        wind_limit_hover_kts=12.0,
        climb_rate_vertical_m_s=2.5,
        descent_rate_vertical_m_s=2.0,
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
        estimated_mtow_kg=31.25,
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
        engineering_notes=[],
        recommendations=[],
        warnings=[],
        metadata={},
    )


@pytest.fixture
def dummy_configuration_result():
    lift = PropulsionLayout(
        lift_system_type="Dedicated Multi-rotor Booms",
        forward_propulsion_layout="Rear Pusher",
        motor_count=4,
        propeller_count=4,
        has_pitch_control=False,
        is_hybrid=False,
        mounting_structure="Composite booms",
    )
    fwd = PropulsionLayout(
        lift_system_type="Dedicated Multi-rotor Booms",
        forward_propulsion_layout="Rear Pusher",
        motor_count=1,
        propeller_count=1,
        has_pitch_control=False,
        is_hybrid=False,
        mounting_structure="Fuselage firewall",
    )
    actuators = ActuatorLayout(
        control_channels_count=9,
        servo_count=4,
        esc_count=5,
        aerodynamic_surface_actuators=["Left Aileron", "Right Aileron", "Elevator", "Rudder"],
        propulsion_actuators=["ESC Lift 1", "ESC Lift 2", "ESC Lift 3", "ESC Lift 4", "ESC Cruise"],
        tilt_actuators=[],
        actuator_placements=[
            {"name": "Lift Motor 1", "x_m": 0.4, "y_m": 0.4, "z_m": 0.0, "type": "lift"},
            {"name": "Lift Motor 2", "x_m": 0.4, "y_m": -0.4, "z_m": 0.0, "type": "lift"},
            {"name": "Lift Motor 3", "x_m": -0.4, "y_m": -0.4, "z_m": 0.0, "type": "lift"},
            {"name": "Lift Motor 4", "x_m": -0.4, "y_m": 0.4, "z_m": 0.0, "type": "lift"},
            {"name": "Cruise Motor", "x_m": -0.6, "y_m": 0.0, "z_m": 0.0, "type": "forward"},
            {"name": "Left Aileron", "x_m": 0.0, "y_m": -0.6, "z_m": 0.0, "type": "surface"},
            {"name": "Right Aileron", "x_m": 0.0, "y_m": 0.6, "z_m": 0.0, "type": "surface"},
        ],
    )
    # Simple dummy modes
    fm = FlightMode(name="Hover", is_active=True, thrust_allocation="Lift", attitude_control="Diff", target_speed_range_kmh=(0, 10), description="")
    fmc = FlightModeConfiguration(hover=fm, takeoff=fm, landing=fm, transition_to_cruise=fm, cruise=fm, transition_to_hover=fm, emergency=fm, recovery=fm)
    analysis = ConfigurationAnalysis(
        mission_suitability=95.0, hover_efficiency=85.0, cruise_efficiency=70.0,
        transition_complexity=45.0, structural_simplicity=80.0, manufacturability=85.0,
        redundancy_score=85.0, maintenance_accessibility=80.0, scalability=75.0,
    )
    return ConfigurationResult(
        selected_configuration=VTOLType.LIFT_CRUISE,
        lift_architecture=lift,
        forward_propulsion_layout=fwd,
        flight_mode_configuration=fmc,
        actuator_layout=actuators,
        configuration_analysis=analysis,
    )


@pytest.fixture
def valid_wing_requirements(dummy_mission_result, dummy_configuration_result):
    return WingRequirements(
        mission_result=dummy_mission_result,
        configuration_result=dummy_configuration_result,
    )


def test_wing_strategy_selection():
    """Verify registry returns correct wing strategy."""
    strategy = VTOLWingStrategyRegistry.get(VTOLMissionCategory.CARGO)
    assert strategy.category == VTOLMissionCategory.CARGO
    assert strategy.default_aspect_ratio == 8.5
    assert strategy.default_wing_loading_kg_m2 == 48.0


def test_wing_validator_failures(valid_wing_requirements):
    """Verify validator flags span violations or placing motors past tip."""
    engine = WingEngine()
    reqs = valid_wing_requirements

    # Case 1: Over-long span
    reqs.preferred_wing_span_m = 6.0
    with pytest.raises(WingValidationError) as excinfo:
        engine.size_wing_system(reqs)
    assert "exceeds physical limit" in str(excinfo.value)

    # Case 2: Aspect ratio out of bounds
    reqs.preferred_wing_span_m = None
    reqs.preferred_aspect_ratio = 22.0
    with pytest.raises(WingValidationError) as excinfo:
        engine.size_wing_system(reqs)
    assert "Aspect ratio must be between" in str(excinfo.value)


def test_wing_engine_flow(valid_wing_requirements):
    """Verify engine coordinates layout, structures, and bending moment analysis."""
    engine = WingEngine()
    result = engine.size_wing_system(valid_wing_requirements)

    assert result is not None
    # check sized dimensions
    assert result.wing_geometry.span_m > 0.0
    assert result.wing_geometry.area_m2 > 0.0

    # check wing chord tapering root > tip
    assert result.wing_geometry.root_chord_m > result.wing_geometry.tip_chord_m

    # check structure
    assert result.wing_structure.estimated_wing_weight_kg > 0.0
    assert result.wing_structure.spar_material is not None

    # check motor mount extraction
    mounts = result.motor_mounts.mounts
    assert len(mounts) == 4  # 4 lift motors should be mapped to the wing
    assert mounts[0].position_y_m == 0.4
    assert mounts[1].position_y_m == -0.4

    # check transition bending moment
    assert result.wing_analysis.transition_bending_moment_nm > 0.0
    assert result.wing_analysis.wing_loading_kg_m2 == pytest.approx(48.0, abs=0.5)
