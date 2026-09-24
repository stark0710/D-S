"""
FinalAircraftDesign Contract Subsystem for Phase 13.

Defines the strongly-typed, comprehensive schema for the normalized output
of all Torq Wings Design Engine pipelines (Fixed-Wing, VTOL, and future Multirotor).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import json

from backend.design.assembly.provenance import ProvenanceCategory, EngineeringStatus, ProvenanceRecord


class AircraftClass(str, Enum):
    FIXED_WING = "FIXED_WING"
    VTOL = "VTOL"
    MULTIROTOR = "MULTIROTOR"


class OverallDesignStatus(str, Enum):
    DESIGN_VALIDATED = "DESIGN_VALIDATED"
    DESIGN_VALIDATED_WITH_DEFERRED_ITEMS = "DESIGN_VALIDATED_WITH_DEFERRED_ITEMS"
    DESIGN_PARTIAL = "DESIGN_PARTIAL"
    DESIGN_FAILED = "DESIGN_FAILED"


# ---------------------------------------------------------------------------
# Requirement Traceability
# ---------------------------------------------------------------------------

@dataclass
class RequirementTraceabilityItem:
    """Explicit mapping from requirement to design outcome with margins."""
    requirement: str
    required_value: Any
    design_value: Any
    unit: str
    limit: Optional[str] = None  # "MIN", "MAX", "EQUAL", "INFO"
    margin: Optional[float] = None
    status: str = "PASS"  # "PASS", "FAIL", "DEFERRED", "NOT_APPLICABLE"
    provenance: ProvenanceCategory = ProvenanceCategory.DERIVED
    source_module: str = ""
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Coordinate System
# ---------------------------------------------------------------------------

@dataclass
class CoordinateSystemContract:
    reference_datum: str = "Aircraft Nose / Leading Edge Root Intersect"
    origin: str = "X=0 (Nose/Datum), Y=0 (Centerline/Symmetry), Z=0 (Waterline)"
    axis_conventions: str = "+X Aft, +Y Right Wingtip, +Z Downward (Aviation Standard)"
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Geometry Contracts
# ---------------------------------------------------------------------------

@dataclass
class WingGeometryContract:
    span_m: float = 0.0
    area_m2: float = 0.0
    aspect_ratio: float = 0.0
    root_chord_m: float = 0.0
    tip_chord_m: float = 0.0
    taper_ratio: float = 0.0
    sweep_deg: float = 0.0
    dihedral_deg: float = 0.0
    incidence_deg: float = 0.0
    mac_m: float = 0.0
    mac_le_x_m: float = 0.0
    airfoil_root: str = ""
    airfoil_tip: str = ""
    spar_locations_chord_pct: List[float] = field(default_factory=lambda: [25.0, 70.0])
    aileron_span_m: Optional[float] = None
    aileron_area_m2: Optional[float] = None
    flap_span_m: Optional[float] = None
    flap_area_m2: Optional[float] = None
    status: EngineeringStatus = EngineeringStatus.VALID


@dataclass
class FuselageGeometryContract:
    length_m: float = 0.0
    max_width_m: float = 0.0
    max_height_m: float = 0.0
    fineness_ratio: float = 0.0
    internal_volume_m3: float = 0.0
    payload_bay_dimensions_m: List[float] = field(default_factory=list)  # [L, W, H]
    battery_bay_dimensions_m: List[float] = field(default_factory=list)  # [L, W, H]
    avionics_bay_dimensions_m: List[float] = field(default_factory=list) # [L, W, H]
    cooling_inlets: str = "Nose ram-air inlet with rear exhaust vents"
    status: EngineeringStatus = EngineeringStatus.VALID


@dataclass
class BoomGeometryContract:
    boom_count: int = 0
    length_m: float = 0.0
    spacing_m: float = 0.0
    cross_section_mm: List[float] = field(default_factory=list)  # [width, height] or [OD, ID]
    attachment_x_locations_m: List[float] = field(default_factory=list)
    status: EngineeringStatus = EngineeringStatus.VALID
    reason: Optional[str] = None


@dataclass
class TailGeometryContract:
    tail_type: str = ""  # "INVERTED_V_TAIL", "CONVENTIONAL", "T_TAIL"
    total_area_m2: float = 0.0
    projected_horizontal_area_m2: float = 0.0
    projected_vertical_area_m2: float = 0.0
    span_m: float = 0.0
    root_chord_m: float = 0.0
    tip_chord_m: float = 0.0
    v_tail_angle_deg: Optional[float] = None
    ruddervator_area_m2: Optional[float] = None
    elevator_area_m2: Optional[float] = None
    rudder_area_m2: Optional[float] = None
    airfoil: str = ""
    status: EngineeringStatus = EngineeringStatus.VALID
    reason: Optional[str] = None


@dataclass
class MultirotorFrameGeometryContract:
    frame_type: str = "DEFERRED"
    arm_count: int = 0
    arm_length_m: float = 0.0
    status: EngineeringStatus = EngineeringStatus.DEFERRED
    reason: str = "Multirotor engineering postponed to future phase"


@dataclass
class GeometryContract:
    wing: WingGeometryContract = field(default_factory=WingGeometryContract)
    fuselage: FuselageGeometryContract = field(default_factory=FuselageGeometryContract)
    booms: BoomGeometryContract = field(default_factory=BoomGeometryContract)
    tail: TailGeometryContract = field(default_factory=TailGeometryContract)
    multirotor_frame: MultirotorFrameGeometryContract = field(default_factory=MultirotorFrameGeometryContract)
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Aerodynamics Contracts
# ---------------------------------------------------------------------------

@dataclass
class AerodynamicsContract:
    cl_cruise: float = 0.0
    cl_max: float = 0.0
    cd0: float = 0.0
    k_induced: float = 0.0
    cd_cruise: float = 0.0
    lift_to_drag_cruise: float = 0.0
    lift_to_drag_max: float = 0.0
    reynolds_number_cruise: float = 0.0
    stall_speed_clean_mps: float = 0.0
    trim_alpha_cruise_deg: float = 0.0
    airfoil_data: Dict[str, Any] = field(default_factory=dict)
    drag_breakdown: Dict[str, float] = field(default_factory=dict)
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Propulsion Contracts
# ---------------------------------------------------------------------------

@dataclass
class PropulsionUnitContract:
    role: str  # "CRUISE", "LIFT"
    motor_model: str = ""
    motor_count: int = 1
    propeller_model: str = ""
    propeller_diameter_in: float = 0.0
    propeller_pitch_in: float = 0.0
    esc_model: str = ""
    esc_rating_a: float = 0.0
    max_thrust_per_motor_n: float = 0.0
    cruise_thrust_per_motor_n: float = 0.0
    cruise_power_electrical_w: float = 0.0
    status: EngineeringStatus = EngineeringStatus.VALID


@dataclass
class LiftPropulsionContract:
    motor_count: int = 0
    motor_model: str = ""
    propeller_model: str = ""
    propeller_diameter_in: float = 0.0
    propeller_pitch_in: float = 0.0
    esc_model: str = "Spedix GS40A"  # Authoritative Phase 8/11 identity
    esc_rating_a: float = 40.0
    total_hover_thrust_required_n: float = 0.0
    hover_thrust_per_motor_n: float = 0.0
    thrust_to_weight_ratio: float = 0.0
    disk_loading_kg_m2: float = 0.0
    hover_power_electrical_w: float = 0.0
    status: EngineeringStatus = EngineeringStatus.VALID
    reason: Optional[str] = None


@dataclass
class PropulsionContract:
    cruise_propulsion: PropulsionUnitContract = field(default_factory=lambda: PropulsionUnitContract(role="CRUISE"))
    lift_propulsion: LiftPropulsionContract = field(default_factory=LiftPropulsionContract)
    total_installed_power_w: float = 0.0
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Transition Contract (VTOL specific)
# ---------------------------------------------------------------------------

@dataclass
class TransitionContract:
    stall_speed_mps: float = 0.0
    safe_transition_speed_mps: float = 0.0
    transition_duration_s: float = 0.0
    vertical_thrust_requirement_n: float = 0.0
    forward_thrust_requirement_n: float = 0.0
    transition_energy_wh: float = 0.0
    reverse_abort_thrust_available: bool = True
    transition_corridor_valid: bool = True
    status: EngineeringStatus = EngineeringStatus.VALID
    reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Energy & Battery Contracts
# ---------------------------------------------------------------------------

@dataclass
class BatteryContract:
    chemistry: str = "LiPo"
    cell_series_count: int = 6  # 6S
    voltage_nominal_v: float = 22.2
    voltage_cutoff_v: float = 19.8
    capacity_mah: float = 0.0
    energy_wh: float = 0.0
    mass_kg: float = 0.0
    continuous_discharge_c: float = 0.0
    max_continuous_current_a: float = 0.0
    installed_count: int = 1
    pack_model: str = ""
    status: EngineeringStatus = EngineeringStatus.VALID


@dataclass
class EnergyContract:
    total_energy_stored_wh: float = 0.0
    energy_required_mission_wh: float = 0.0
    energy_reserve_pct: float = 0.0
    hover_energy_wh: float = 0.0
    cruise_energy_wh: float = 0.0
    transition_energy_wh: float = 0.0
    avionics_energy_wh: float = 0.0
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Mass Properties Contracts
# ---------------------------------------------------------------------------

@dataclass
class ComponentMassItem:
    name: str
    category: str
    mass_kg: float
    x_cg_m: float
    y_cg_m: float
    z_cg_m: float
    provenance: ProvenanceCategory = ProvenanceCategory.CALCULATED


@dataclass
class InertiaTensorContract:
    ixx_kg_m2: Optional[float] = None
    iyy_kg_m2: Optional[float] = None
    izz_kg_m2: Optional[float] = None
    ixz_kg_m2: Optional[float] = None
    status: EngineeringStatus = EngineeringStatus.DEFERRED
    reason: str = "Detailed solid-body inertia tensor deferred to 3D CAD mass properties compilation."


@dataclass
class MassPropertiesContract:
    mtow_kg: float = 0.0
    empty_mass_kg: float = 0.0
    payload_mass_kg: float = 0.0
    battery_mass_kg: float = 0.0
    structural_mass_kg: float = 0.0
    propulsion_mass_kg: float = 0.0
    avionics_mass_kg: float = 0.0
    wiring_harness_mass_kg: float = 0.0
    cg_x_m: float = 0.0
    cg_y_m: float = 0.0
    cg_z_m: float = 0.0
    forward_cg_limit_x_m: float = 0.0
    aft_cg_limit_x_m: float = 0.0
    cg_margin_m: float = 0.0
    component_breakdown: List[ComponentMassItem] = field(default_factory=list)
    inertia: InertiaTensorContract = field(default_factory=InertiaTensorContract)
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Stability & Controls Contracts
# ---------------------------------------------------------------------------

@dataclass
class StabilityContract:
    neutral_point_x_m: float = 0.0
    neutral_point_mac_pct: float = 0.0
    static_margin_mac_pct: float = 0.0
    static_margin_m: float = 0.0
    c_m_alpha_per_rad: float = 0.0
    c_n_beta_per_rad: float = 0.0
    c_l_beta_per_rad: float = 0.0
    is_longitudinally_stable: bool = True
    is_directionally_stable: bool = True
    is_laterally_stable: bool = True
    status: EngineeringStatus = EngineeringStatus.VALID
    reason: Optional[str] = None


@dataclass
class ControlsContract:
    c_m_delta_e_per_rad: float = 0.0
    c_n_delta_r_per_rad: float = 0.0
    c_l_delta_a_per_rad: float = 0.0
    pitch_authority_nm: float = 0.0
    yaw_authority_nm: float = 0.0
    roll_authority_nm: float = 0.0
    trim_elevator_cruise_deg: float = 0.0
    max_elevator_deflection_deg: float = 25.0
    max_aileron_deflection_deg: float = 20.0
    max_rudder_deflection_deg: float = 25.0
    trim_feasible: bool = True
    status: EngineeringStatus = EngineeringStatus.VALID
    reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Performance Contract
# ---------------------------------------------------------------------------

@dataclass
class PerformanceContract:
    cruise_speed_kmh: float = 0.0
    cruise_speed_mps: float = 0.0
    stall_speed_kmh: float = 0.0
    max_speed_kmh: float = 0.0
    cruise_altitude_m: float = 0.0
    range_km: float = 0.0
    endurance_min: float = 0.0
    hover_endurance_min: float = 0.0
    climb_rate_max_mps: float = 0.0
    service_ceiling_m: float = 0.0
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Avionics & Electrical Contracts
# ---------------------------------------------------------------------------

@dataclass
class AvionicsContract:
    flight_controller: str = "Holybro Pixhawk 6X"
    autopilot_firmware: str = "ArduPilot (QuadPlane / Plane)"
    gnss_module: str = "Holybro H-RTK F9P Helical"
    airspeed_sensor: str = "Sensirion SDP33 Digital Airspeed"
    telemetry_radio: str = "Holybro Telemetry 433/915MHz"
    rc_receiver: str = "ExpressLRS 2.4GHz Diversity"
    companion_computer: str = "Raspberry Pi 4 Model B (4GB)"
    status: EngineeringStatus = EngineeringStatus.VALID


@dataclass
class ElectricalContract:
    main_bus_voltage_v: float = 22.2
    avionics_bus_voltage_v: float = 5.3
    max_continuous_current_a: float = 0.0
    peak_current_a: float = 0.0
    power_distribution_board: str = "Custom / Integrated PDB with 5V/12V Regulators"
    power_module: str = "Holybro PM02D Digital Power Module"
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Commercial Components BOM Contract
# ---------------------------------------------------------------------------

@dataclass
class CommercialComponentItem:
    category: str
    role: str
    manufacturer: str
    model: str
    part_number: Optional[str] = None
    quantity: int = 1
    mass_per_unit_kg: float = 0.0
    total_mass_kg: float = 0.0
    voltage_rating_v: Optional[float] = None
    max_current_a: Optional[float] = None
    rated_power_w: Optional[float] = None
    mounting_type: str = "Direct / Carbon Bracket"
    verification_status: str = "COMMERCIAL_COMPONENT_VERIFIED"
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Installation & Manufacturing Contracts
# ---------------------------------------------------------------------------

@dataclass
class InstallationContract:
    battery_mounting: str = "Quick-release carbon tray with Velcro retention strap"
    payload_mounting: str = "Bottom fuselage bay with vibration-isolated carbon plate"
    avionics_mounting: str = "Damped internal tray at centerline"
    cooling_provisions: str = "Direct airflow over ESC heat sinks and battery bay"
    status: EngineeringStatus = EngineeringStatus.VALID


@dataclass
class ManufacturingContract:
    wing_construction: str = "Molded Carbon Fiber Composite / CNC Machined Foam Core"
    fuselage_construction: str = "Carbon Fiber Monocoque with Airex Foam Core"
    spar_material: str = "Pultruded Carbon Fiber Tube"
    tail_construction: str = "Solid Core Composite / Carbon Skin"
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Constraints & Assumptions Contracts
# ---------------------------------------------------------------------------

@dataclass
class ConstraintsContract:
    max_allowable_mtow_kg: float = 0.0
    max_wingspan_m: float = 0.0
    min_endurance_min: float = 0.0
    min_range_km: float = 0.0
    battery_reserve_min_pct: float = 20.0
    structural_limit_load_factor_g: float = 3.8
    structural_ultimate_factor: float = 1.5
    status: EngineeringStatus = EngineeringStatus.VALID


@dataclass
class AssumptionsContract:
    air_density_kg_m3: float = 1.225
    gravity_m_s2: float = 9.80665
    motor_efficiency: float = 0.85
    esc_efficiency: float = 0.95
    propeller_efficiency_cruise: float = 0.72
    propeller_figure_of_merit_hover: float = 0.70
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# CAD Handover Contract
# ---------------------------------------------------------------------------

@dataclass
class CADHandoverContract:
    coordinate_system: CoordinateSystemContract = field(default_factory=CoordinateSystemContract)
    reference_datum: str = "X=0 at Nose tip, Y=0 Aircraft centerline, Z=0 Fuselage waterline"
    major_geometry: Dict[str, Any] = field(default_factory=dict)
    wing_airfoils: List[str] = field(default_factory=list)
    tail_airfoil: str = ""
    control_surfaces: Dict[str, Any] = field(default_factory=dict)
    component_envelopes: List[Dict[str, Any]] = field(default_factory=list)
    mounting_coordinates: Dict[str, List[float]] = field(default_factory=dict)
    cg_location_m: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Simulation Handover Contract
# ---------------------------------------------------------------------------

@dataclass
class SimulationHandoverContract:
    mtow_kg: float = 0.0
    empty_mass_kg: float = 0.0
    payload_mass_kg: float = 0.0
    battery_mass_kg: float = 0.0
    cg_m: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    inertia: InertiaTensorContract = field(default_factory=InertiaTensorContract)
    aerodynamics_polar: Dict[str, float] = field(default_factory=dict)
    stability_derivatives: Dict[str, float] = field(default_factory=dict)
    control_derivatives: Dict[str, float] = field(default_factory=dict)
    control_limits_deg: Dict[str, float] = field(default_factory=dict)
    propulsion_parameters: Dict[str, Any] = field(default_factory=dict)
    trim_conditions: Dict[str, Any] = field(default_factory=dict)
    status: EngineeringStatus = EngineeringStatus.VALID


# ---------------------------------------------------------------------------
# Validation Status Contract
# ---------------------------------------------------------------------------

@dataclass
class ValidationStatusContract:
    design_validated: bool = True
    commercial_component_verified: bool = True
    physical_ground_validated: bool = True
    flight_validated: bool = False  # NEVER True in Phase 13 per Section 10
    flight_status_note: str = "DESIGN AND BENCH VALIDATED ONLY. FLIGHT TEST ENVELOPE NOT ESTABLISHED."
    status: str = "PHYSICAL_GROUND_VALIDATED"


# ---------------------------------------------------------------------------
# Root Final Aircraft Design Contract
# ---------------------------------------------------------------------------

@dataclass
class FinalAircraftDesign:
    """
    Unified Master Design Contract for Torq Wings Design Engine.
    Exposes all authoritative sizing, geometry, mass, aero, propulsion,
    traceability, and handover specifications.
    """
    design_id: str
    aircraft_class: AircraftClass
    configuration: str
    mission: Dict[str, Any]
    technical_requirements: Dict[str, Any]
    coordinate_system: CoordinateSystemContract
    geometry: GeometryContract
    aerodynamics: AerodynamicsContract
    propulsion: PropulsionContract
    transition: TransitionContract
    energy: EnergyContract
    battery: BatteryContract
    mass_properties: MassPropertiesContract
    stability: StabilityContract
    controls: ControlsContract
    performance: PerformanceContract
    avionics: AvionicsContract
    electrical: ElectricalContract
    commercial_components: List[CommercialComponentItem]
    installation: InstallationContract
    manufacturing: ManufacturingContract
    constraints: ConstraintsContract
    assumptions: AssumptionsContract
    provenance: Dict[str, ProvenanceRecord]
    requirement_traceability: List[RequirementTraceabilityItem]
    cad_handover: CADHandoverContract
    simulation_handover: SimulationHandoverContract
    validation_status: ValidationStatusContract
    design_status: OverallDesignStatus = OverallDesignStatus.DESIGN_VALIDATED

    def to_dict(self) -> Dict[str, Any]:
        """Recursively serializes FinalAircraftDesign to JSON-serializable dictionary."""
        from backend.design.assembly.report_generator import to_dict_deterministic
        return to_dict_deterministic(self)

    def to_json(self, indent: int = 2) -> str:
        """Serializes FinalAircraftDesign to deterministic JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
