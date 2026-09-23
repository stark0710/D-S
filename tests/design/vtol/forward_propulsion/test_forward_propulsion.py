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
    AirfoilResult,
    PolarAnalysis,
    TransitionAnalysis,
    StallAnalysis,
    ManufacturingAnalysis,
)
from backend.design.vtol.tail import (
    TailResult,
    TailGeometry,
    TailStructure,
    TailControls,
    TailStabilityAnalysis,
    TailControlAnalysis,
)
from backend.design.vtol.fuselage import (
    FuselageResult,
    FuselageGeometry,
    FuselageStructure,
    InternalLayout,
    CompartmentLayout,
    Compartment,
    MountingInterfaces,
    MountingInterface,
    CoolingLayout,
    FuselageAnalysis,
)
from backend.design.vtol.lift_system import (
    LiftSystemResult,
    HoverThrustAnalysis,
    LiftPowerAnalysis,
    LiftRedundancyAnalysis,
    LiftSystemAnalysis,
    LiftRotorLayout,
)
from backend.design.vtol.forward_propulsion import (
    ForwardPropulsionRequirements,
    ForwardPropulsionEngine,
    ForwardPropulsionValidator,
    ForwardPropulsionValidationError,
    VTOLForwardPropulsionStrategyRegistry,
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
        cruise_speed_kmh=90.0,
        cruise_altitude_m=150.0,
        cruise_range_km=30.0,
        cruise_endurance_min=20.0,
        wind_limit_cruise_kts=18.0,
    )
    profile = MissionProfile(
        mission_category=VTOLMissionCategory.CARGO,
        vtol_type=VTOLType.LIFT_CRUISE,
        payload_kg=10.0,
        total_endurance_min=25.0,
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
        estimated_mtow_kg=30.0,
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
        actuator_placements=[],
    )
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
        area_m2=0.65,
        aspect_ratio=9.6,
        sweep_deg=0.0,
        dihedral_deg=1.5,
        anhedral_deg=0.0,
        incidence_deg=2.0,
        washout_deg=1.5,
        taper_ratio=0.6,
        root_chord_m=0.32,
        tip_chord_m=0.19,
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
def dummy_airfoil_result():
    geom = {
        "thickness_ratio": 0.12,
        "camber": 0.04,
        "le_radius": 0.016,
        "max_thickness_loc": 0.30,
        "max_camber_loc": 0.40,
        "cm0": -0.09,
    }
    polar = PolarAnalysis(
        cl_cruise=0.48,
        cd_cruise=0.0125,
        lift_to_drag_ratio_sectional=32.8,
        pitching_moment_cruise=-0.09,
        slipstream_correction_factor=1.15,
    )
    trans = TransitionAnalysis(
        transition_aoa_range_deg=(0, 18),
        flow_detachment_angle_deg=19.0,
        separated_flow_drag_coefficient=1.12,
        pitch_stability_margin_transition=0.24,
        suitability_rating="Excellent",
    )
    stall = StallAnalysis(
        cl_max=1.45,
        stall_angle_deg=18.0,
        downwash_velocity_m_s=7.5,
        downwash_angle_deg=14.5,
        stall_behavior="Gentle",
    )
    mfg = ManufacturingAnalysis(
        foam_cut_feasibility_score=90.0,
        mold_release_feasibility_score=85.0,
        min_trailing_edge_thickness_mm=1.8,
        carbon_spar_diameter_max_mm=29.2,
        suitability_rating="Excellent",
    )
    return AirfoilResult(
        selected_airfoil="NACA 4412",
        airfoil_geometry=geom,
        polar_analysis=polar,
        transition_analysis=trans,
        stall_analysis=stall,
        manufacturing_analysis=mfg,
    )


@pytest.fixture
def dummy_tail_result():
    geom = TailGeometry(
        tail_configuration="Twin Boom Tail",
        tail_arm_m=0.8,
        horizontal_area_m2=0.12,
        horizontal_span_m=0.65,
        horizontal_aspect_ratio=3.5,
        vertical_area_m2=0.06,
        vertical_span_m=0.31,
        vertical_aspect_ratio=1.6,
        v_tail_angle_deg=0.0,
    )
    struct = TailStructure(
        structural_concept="Carbon booms",
        estimated_tail_weight_kg=0.45,
        boom_diameter_mm=30.0,
        boom_material="Carbon fiber",
    )
    controls = TailControls(
        elevator_area_m2=0.03,
        elevator_span_m=0.65,
        rudder_area_m2=0.018,
        rudder_span_m=0.31,
        control_mixing_type="Conventional",
    )
    stab = TailStabilityAnalysis(
        longitudinal_stability_score=90.0,
        directional_stability_score=88.0,
        static_margin_percent=15.0,
        neutral_point_percent=40.0,
        trim_capability_deg=2.5,
    )
    ctrl = TailControlAnalysis(
        pitch_effectiveness=75.0,
        yaw_effectiveness=75.0,
        transition_authority=80.0,
        rotor_downwash_interference_index=0.35,
        slipstream_influence_factor=1.25,
        hover_mode_control_authority=0.0,
    )
    return TailResult(
        tail_geometry=geom,
        tail_structure=struct,
        control_surfaces=controls,
        stability_analysis=stab,
        control_analysis=ctrl,
    )


@pytest.fixture
def dummy_fuselage_result():
    geom = FuselageGeometry(
        fuselage_type="Box Fuselage",
        length_m=2.5,
        width_m=0.35,
        height_m=0.42,
        cross_section_shape="Rectangular",
        volume_m3=0.28,
        wetted_area_m2=4.0,
        frontal_area_m2=0.15,
    )
    struct = FuselageStructure(
        construction_type="Composite Shell Monocoque",
        estimated_fuselage_weight_kg=4.5,
        wall_thickness_mm=1.2,
        reinforcement_locations=[],
        crash_energy_absorption_level="High",
    )
    comp = Compartment(name="A", volume_m3=0.1, length_m=0.5, width_m=0.3, height_m=0.3, position_x_m=0.5, is_accessible=True)
    comp_layout = CompartmentLayout(battery_bay=comp, payload_bay=comp, avionics_bay=comp)
    internal = InternalLayout(placements=[], packaging_efficiency=60.0, center_of_gravity_x_m=1.25)
    mounts = MountingInterfaces(wing_attachment=MountingInterface(name="", type="", location_x_m=1.1, location_y_m=0.0, location_z_m=0.2, bolt_circle_diameter_mm=10.0, load_limit_n=1500.0))
    cooling = CoolingLayout(inlets=[], has_active_cooling=False, estimated_cooling_effectiveness=80.0)
    analysis = FuselageAnalysis(
        structural_efficiency=85.0, packaging_efficiency=60.0, aerodynamic_drag_coefficient_cd0=0.015,
        cg_offset_from_wing_mac_percent=2.5, cooling_effectiveness_score=80.0, maintenance_accessibility_score=80.0,
        manufacturability_score=80.0, modularity_score=70.0, weight_efficiency=85.0,
    )
    return FuselageResult(
        fuselage_geometry=geom,
        structural_layout=struct,
        internal_layout=internal,
        compartment_layout=comp_layout,
        mounting_interfaces=mounts,
        cooling_layout=cooling,
        engineering_analysis=analysis,
    )


@pytest.fixture
def dummy_lift_system_result():
    hover = HoverThrustAnalysis(required_hover_thrust_n=450.0, available_hover_thrust_n=600.0, thrust_to_weight_ratio=1.45, thrust_margin_n=150.0)
    power = LiftPowerAnalysis(hover_total_power_kw=6.5, hover_total_current_a=146.0, hover_energy_consumption_kwh=0.6, esc_current_draw_a=36.5, battery_c_rate_required=28.0)
    redundancy = LiftRedundancyAnalysis(redundancy_level="Single Motor Out Controllable", has_engine_out_capability=True, motor_out_thrust_reserve_fraction=0.15, failure_scenarios_tested=[])
    analysis = LiftSystemAnalysis(disk_loading_n_m2=85.0, power_loading_n_w=0.09, hover_efficiency_g_w=7.4, rotor_interference_loss_factor=0.0, noise_level_db=84.0, manufacturability_score=80.0, fault_tolerance_score=80.0)
    layout = LiftRotorLayout(rotors=[], rotor_spacing_m=0.65, distributed_propulsion_active=False)
    return LiftSystemResult(
        lift_motor_selection={},
        lift_propeller_selection={},
        rotor_layout=layout,
        hover_analysis=hover,
        power_analysis=power,
        redundancy_analysis=redundancy,
        engineering_analysis=analysis,
    )


@pytest.fixture
def valid_forward_requirements(dummy_mission_result, dummy_configuration_result, dummy_wing_result, dummy_airfoil_result, dummy_tail_result, dummy_fuselage_result, dummy_lift_system_result):
    return ForwardPropulsionRequirements(
        mission_result=dummy_mission_result,
        configuration_result=dummy_configuration_result,
        wing_result=dummy_wing_result,
        airfoil_result=dummy_airfoil_result,
        tail_result=dummy_tail_result,
        fuselage_result=dummy_fuselage_result,
        lift_system_result=dummy_lift_system_result,
    )


def test_forward_strategy_selection():
    """Verify registry returns correct strategy for Cargo forward designs."""
    strategy = VTOLForwardPropulsionStrategyRegistry.get(VTOLMissionCategory.CARGO)
    assert strategy.category == VTOLMissionCategory.CARGO
    assert strategy.default_propulsion_architecture == "Twin Tractor"
    assert strategy.default_climb_power_factor == 1.45


def test_forward_engine_flow(valid_forward_requirements):
    """Verify motor selection, drag sizing, cruise power, rate of climb, and max speed."""
    engine = ForwardPropulsionEngine()
    result = engine.design_forward_propulsion(valid_forward_requirements)

    assert result is not None
    # check selected motor and propeller specs
    assert result.motor_selection["name"] == "T-Motor MN5008"
    assert result.propeller_selection["name"] == "T-Motor 15x5 CF"
    assert result.esc_selection["name"] == "Hobbywing XRotor 40A"

    # check drag & thrust margins
    assert result.cruise_analysis.required_thrust_n > 0.0
    assert result.cruise_analysis.available_thrust_n >= result.cruise_analysis.required_thrust_n

    # check power and battery draw
    assert result.power_analysis.required_cruise_power_w > 0.0
    assert result.power_analysis.current_draw_a > 0.0

    # check clearances and layout
    assert len(result.propulsion_layout.placements) == 2
    assert result.propulsion_layout.architecture == "Twin Tractor"

    # check performance limits
    assert result.performance_analysis.max_speed_kmh > 90.0  # exceeds cruise speed
    assert result.performance_analysis.rate_of_climb_m_s >= 1.5


def test_forward_validator_failures(valid_forward_requirements):
    """Verify validator flags insufficient climb capabilities."""
    engine = ForwardPropulsionEngine()
    reqs = valid_forward_requirements

    # Alter requirements to enforce a very high minimum climb rate limit of 15.0 m/s
    reqs.metadata["min_climb_rate"] = 15.0

    with pytest.raises(ForwardPropulsionValidationError) as excinfo:
        engine.design_forward_propulsion(reqs)
    assert "Climb capability violation" in str(excinfo.value)
