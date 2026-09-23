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
    WingResult,
    WingGeometry,
    WingStructure,
    MotorMounts,
    WingAnalysis,
)
from backend.design.vtol.airfoil import (
    AirfoilRequirements,
    AirfoilEngine,
    AirfoilValidator,
    AirfoilValidationError,
    VTOLAirfoilStrategyRegistry,
    AirfoilDatabase,
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
def dummy_wing_result():
    geom = WingGeometry(
        wing_type="High Wing",
        span_m=2.5,
        area_m2=0.651,
        aspect_ratio=9.6,
        sweep_deg=0.0,
        dihedral_deg=1.5,
        anhedral_deg=0.0,
        incidence_deg=2.0,
        washout_deg=1.5,
        taper_ratio=0.6,
        root_chord_m=0.325,  # thick root chord
        tip_chord_m=0.195,
        wing_position="High Wing",
    )
    struct = WingStructure(
        structural_concept="Double spar carbon",
        estimated_wing_weight_kg=1.8,
        limit_load_factor_g=4.0,
        ultimate_load_factor_g=6.0,
        spar_material="Carbon fiber",
    )
    analysis = WingAnalysis(
        wing_loading_kg_m2=48.0,
        cruise_lift_coefficient=0.48,
        stall_speed_cruise_configuration_kmh=45.0,
        cruise_efficiency=75.0,
        hover_structural_loading=3.1,
        transition_bending_moment_nm=24.5,
        structural_efficiency=94.2,
        manufacturability_score=85.0,
        motor_integration_score=85.0,
        maintenance_accessibility_score=80.0,
    )
    return WingResult(
        wing_geometry=geom,
        wing_structure=struct,
        motor_mounts=MotorMounts(mounts=[], has_tilt_mechanism=False, tilt_servo_torque_nm=0.0),
        wing_analysis=analysis,
    )


@pytest.fixture
def valid_airfoil_requirements(dummy_mission_result, dummy_configuration_result, dummy_wing_result):
    return AirfoilRequirements(
        mission_result=dummy_mission_result,
        configuration_result=dummy_configuration_result,
        wing_result=dummy_wing_result,
    )


def test_airfoil_strategy_selection():
    """Verify registry returns correct strategy for long endurance airfoil tasks."""
    strategy = VTOLAirfoilStrategyRegistry.get(VTOLMissionCategory.LONG_ENDURANCE)
    assert strategy.category == VTOLMissionCategory.LONG_ENDURANCE
    assert "MH 32" in strategy.preferred_candidates
    assert strategy.target_cl == 0.55


def test_airfoil_engine_flow(valid_airfoil_requirements):
    """Verify selection, dynamic pressure corrections, and lift coefficients."""
    engine = AirfoilEngine()
    result = engine.design_airfoil(valid_airfoil_requirements)

    assert result is not None
    # Cargo category -> Selig S1223
    assert result.selected_airfoil == "Selig S1223"
    assert result.airfoil_geometry["thickness_ratio"] == 0.122
    assert result.airfoil_geometry["camber"] == 0.081

    # polar check
    assert result.polar_analysis.slipstream_correction_factor == 1.15  # lift cruise has forward propulsion slipstream
    assert result.polar_analysis.cl_cruise < 0.48  # corrected Cl is smaller than wing lift coefficient due to slipstream factor
    assert result.polar_analysis.cd_cruise > 0.0

    # transition check
    assert result.transition_analysis.flow_detachment_angle_deg > 15.0

    # stall downwash check
    assert result.stall_analysis.cl_max == 1.95
    assert result.stall_analysis.downwash_velocity_m_s > 0.0

    # manufacturing/packaging checks
    assert result.manufacturing_analysis.carbon_spar_diameter_max_mm > 0.0
    assert result.manufacturing_analysis.foam_cut_feasibility_score == 70.0  # Selig has low wire-cut feasibility


def test_airfoil_validator_failures(valid_airfoil_requirements):
    """Verify validator catches root chord thickness conflicts with spar diameters."""
    engine = AirfoilEngine()
    reqs = valid_airfoil_requirements

    # Alter wing root chord to be very small, making the wing root too thin for the spar
    reqs.wing_result.wing_geometry.root_chord_m = 0.05
    with pytest.raises(AirfoilValidationError) as excinfo:
        engine.design_airfoil(reqs)
    assert "too thin to structural spar" in str(excinfo.value)
