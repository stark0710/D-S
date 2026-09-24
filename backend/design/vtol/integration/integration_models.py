"""
VTOL Phase 9 System Integration & Verification — Domain Models.

Purpose:
    Typed dataclasses defining hardware assignment, electrical architecture,
    I/O pinout allocation, physical installation, integrated CG, mass reconciliation,
    mission-state operational integration, preliminary failure modes (FMEA),
    and comprehensive verification statuses for the Torq Wings Lift + Cruise (QuadPlane).

Standards:
    - Downstream of Phases 1-8: strictly consumes authoritative outputs without mutation.
    - Explicit provenance tagging on every calculated, verified, or assumed metric.
    - Zero specification fabrication: unsupported items marked DEFERRED or INSUFFICIENT_INPUT.
    - Recursive JSON serializability for all models.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IntegrationStatus(str, Enum):
    """Authoritative integration verification final states (Prompt Section 20)."""
    INTEGRATION_COMPLETE = "INTEGRATION_COMPLETE"
    INTEGRATION_COMPLETE_WITH_WARNINGS = "INTEGRATION_COMPLETE_WITH_WARNINGS"
    INTEGRATION_INCOMPLETE = "INTEGRATION_INCOMPLETE"
    INTEGRATION_FAILED = "INTEGRATION_FAILED"


class ProvenanceCategory(str, Enum):
    """Authoritative provenance classification taxonomy (Prompt Section 2 & 26)."""
    DERIVED = "DERIVED"
    UPSTREAM_RESULT = "UPSTREAM_RESULT"
    COMMERCIAL_VERIFIED = "COMMERCIAL_VERIFIED"
    CONFIGURABLE_ASSUMPTION = "CONFIGURABLE_ASSUMPTION"
    PROJECT_REQUIREMENT = "PROJECT_REQUIREMENT"
    DEFERRED = "DEFERRED"
    INSUFFICIENT_INPUT = "INSUFFICIENT_INPUT"
    FAIL = "FAIL"


class VerificationCheckStatus(str, Enum):
    """Individual integration check status (Prompt Section 7)."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    DEFERRED = "DEFERRED"
    INSUFFICIENT_INPUT = "INSUFFICIENT_INPUT"


class AircraftRole(str, Enum):
    """Functional role taxonomy within the Lift + Cruise aircraft (Prompt Section 5)."""
    VTOL_MOTOR_1 = "VTOL_MOTOR_1"  # Front-Left
    VTOL_MOTOR_2 = "VTOL_MOTOR_2"  # Front-Right
    VTOL_MOTOR_3 = "VTOL_MOTOR_3"  # Rear-Left
    VTOL_MOTOR_4 = "VTOL_MOTOR_4"  # Rear-Right
    VTOL_PROP_1 = "VTOL_PROP_1"
    VTOL_PROP_2 = "VTOL_PROP_2"
    VTOL_PROP_3 = "VTOL_PROP_3"
    VTOL_PROP_4 = "VTOL_PROP_4"
    VTOL_ESC_1 = "VTOL_ESC_1"
    VTOL_ESC_2 = "VTOL_ESC_2"
    VTOL_ESC_3 = "VTOL_ESC_3"
    VTOL_ESC_4 = "VTOL_ESC_4"
    CRUISE_MOTOR = "CRUISE_MOTOR"
    CRUISE_PROP = "CRUISE_PROP"
    CRUISE_ESC = "CRUISE_ESC"
    BATTERY_MAIN = "BATTERY_MAIN"
    POWER_DISTRIBUTION = "POWER_DISTRIBUTION"
    LEFT_AILERON_SERVO = "LEFT_AILERON_SERVO"
    RIGHT_AILERON_SERVO = "RIGHT_AILERON_SERVO"
    VTAIL_SURFACE_1_SERVO = "VTAIL_SURFACE_1_SERVO"  # Ruddervator Left
    VTAIL_SURFACE_2_SERVO = "VTAIL_SURFACE_2_SERVO"  # Ruddervator Right
    AUTOPILOT_PIXHAWK = "AUTOPILOT_PIXHAWK"
    NAVIGATION_GNSS_RTK = "NAVIGATION_GNSS_RTK"
    DIGITAL_AIRSPEED = "DIGITAL_AIRSPEED"
    TELEMETRY_TRANSCEIVER = "TELEMETRY_TRANSCEIVER"
    RC_RECEIVER = "RC_RECEIVER"
    COMPANION_SBC = "COMPANION_SBC"
    MISSION_PAYLOAD_CAMERA = "MISSION_PAYLOAD_CAMERA"


class BusType(str, Enum):
    """Electrical power bus topology classification."""
    HIGH_VOLTAGE_MAIN_22V = "HIGH_VOLTAGE_MAIN_22V"  # 6S LiPo Direct
    REGULATED_5V_AVIONICS = "REGULATED_5V_AVIONICS"    # 5.0V BEC Main Rail
    REGULATED_5V_COMPANION = "REGULATED_5V_COMPANION"  # 5.0V BEC SBC Rail
    REGULATED_12V_PAYLOAD = "REGULATED_12V_PAYLOAD"    # 12.0V BEC Aux Rail


class IOPortType(str, Enum):
    """Pixhawk 6X port classification (Prompt Section 8)."""
    PWM_MAIN_OUTPUT = "PWM_MAIN_OUTPUT"
    PWM_AUX_OUTPUT = "PWM_AUX_OUTPUT"
    UART_SERIAL = "UART_SERIAL"
    I2C_BUS = "I2C_BUS"
    CAN_BUS = "CAN_BUS"
    SPI_BUS = "SPI_BUS"
    POWER_MONITOR = "POWER_MONITOR"
    RC_INPUT = "RC_INPUT"


class SignalProtocol(str, Enum):
    """Control and communication protocol."""
    PWM = "PWM"
    DSHOT600 = "DSHOT600"
    UART_MAVLINK = "UART_MAVLINK"
    UART_NMEA_UBX = "UART_NMEA_UBX"
    I2C_SENSOR = "I2C_SENSOR"
    DRONECAN = "DRONECAN"
    CRSF = "CRSF"
    SBUS = "SBUS"
    ANALOG_VOLTAGE_CURRENT = "ANALOG_VOLTAGE_CURRENT"
    DISCRETE_GPIO = "DISCRETE_GPIO"


class MountingRegion(str, Enum):
    """Physical airframe compartment or structural mounting zone."""
    NOSE_AVIONICS_BAY = "NOSE_AVIONICS_BAY"
    FUSELAGE_CENTER_BAY = "FUSELAGE_CENTER_BAY"
    FUSELAGE_AFT_BAY = "FUSELAGE_AFT_BAY"
    FUSELAGE_FIREWALL = "FUSELAGE_FIREWALL"
    WING_LEFT_INBOARD = "WING_LEFT_INBOARD"
    WING_RIGHT_INBOARD = "WING_RIGHT_INBOARD"
    WING_LEFT_OUTBOARD = "WING_LEFT_OUTBOARD"
    WING_RIGHT_OUTBOARD = "WING_RIGHT_OUTBOARD"
    BOOM_LEFT_FRONT = "BOOM_LEFT_FRONT"
    BOOM_LEFT_AFT = "BOOM_LEFT_AFT"
    BOOM_RIGHT_FRONT = "BOOM_RIGHT_FRONT"
    BOOM_RIGHT_AFT = "BOOM_RIGHT_AFT"
    TAIL_LEFT_FIN = "TAIL_LEFT_FIN"
    TAIL_RIGHT_FIN = "TAIL_RIGHT_FIN"


class MissionState(str, Enum):
    """10-Phase QuadPlane mission states (Prompt Section 13)."""
    GROUND_PREFLIGHT = "GROUND_PREFLIGHT"
    VTOL_TAKEOFF = "VTOL_TAKEOFF"
    HOVER_CLIMB = "HOVER_CLIMB"
    TRANSITION_TO_CRUISE = "TRANSITION_TO_CRUISE"
    FIXED_WING_CRUISE = "FIXED_WING_CRUISE"
    MISSION_LOITER = "MISSION_LOITER"
    TRANSITION_TO_VTOL = "TRANSITION_TO_VTOL"
    HOVER_DESCENT = "HOVER_DESCENT"
    VTOL_LANDING = "VTOL_LANDING"
    GROUND_POSTFLIGHT = "GROUND_POSTFLIGHT"


class ControllabilityStatus(str, Enum):
    """Post-failure controllability classification (Audit Section 5)."""
    VERIFIED = "VERIFIED"
    ANALYTICALLY_SUPPORTED = "ANALYTICALLY_SUPPORTED"
    CONFIGURATION_SUPPORTED = "CONFIGURATION_SUPPORTED"
    DEFERRED = "DEFERRED"
    INSUFFICIENT_INPUT = "INSUFFICIENT_INPUT"
    NOT_ANALYZED = "NOT_ANALYZED"


# =========================================================================
# 1. HARDWARE ASSIGNMENT MODEL
# =========================================================================

@dataclass(slots=True)
class HardwareAssignment:
    """
    Mapping of a commercial BOM item to a discrete aircraft functional role (Prompt Section 5).
    """
    assignment_id: str
    role: AircraftRole
    bom_id: str
    category: str
    manufacturer: str
    model: str
    quantity: int
    unit_mass_kg: float
    total_mass_kg: float
    power_requirement_w: Optional[float]
    voltage_v: Optional[float]
    interface_type: str
    notes: str = ""
    provenance: ProvenanceCategory = ProvenanceCategory.COMMERCIAL_VERIFIED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assignment_id": self.assignment_id,
            "role": self.role.value,
            "bom_id": self.bom_id,
            "category": self.category,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "quantity": self.quantity,
            "unit_mass_kg": round(self.unit_mass_kg, 4),
            "total_mass_kg": round(self.total_mass_kg, 4),
            "power_requirement_w": round(self.power_requirement_w, 2) if self.power_requirement_w is not None else None,
            "voltage_v": round(self.voltage_v, 2) if self.voltage_v is not None else None,
            "interface_type": self.interface_type,
            "notes": self.notes,
            "provenance": self.provenance.value,
        }


# =========================================================================
# 2. ELECTRICAL ARCHITECTURE & POWER MODELS
# =========================================================================

@dataclass(slots=True)
class ElectricalLoad:
    """A discrete electrical consumer on a specific bus."""
    load_id: str
    load_name: str
    role: AircraftRole
    bus_type: BusType
    voltage_nominal_v: float
    continuous_current_a: float
    peak_current_a: float
    continuous_power_w: float
    peak_power_w: float
    provenance: ProvenanceCategory
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "load_id": self.load_id,
            "load_name": self.load_name,
            "role": self.role.value,
            "bus_type": self.bus_type.value,
            "voltage_nominal_v": round(self.voltage_nominal_v, 2),
            "continuous_current_a": round(self.continuous_current_a, 2),
            "peak_current_a": round(self.peak_current_a, 2),
            "continuous_power_w": round(self.continuous_power_w, 2),
            "peak_power_w": round(self.peak_power_w, 2),
            "provenance": self.provenance.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class ElectricalBus:
    """A distinct electrical bus/rail in the power distribution tree."""
    bus_type: BusType
    bus_name: str
    nominal_voltage_v: float
    voltage_min_v: float
    voltage_max_v: float
    max_continuous_current_capacity_a: float
    max_peak_current_capacity_a: float
    regulator_model: Optional[str]
    source_bus: Optional[BusType]
    loads: List[ElectricalLoad] = field(default_factory=list)
    total_continuous_current_a: float = 0.0
    total_peak_current_a: float = 0.0
    continuous_margin_a: float = 0.0
    peak_margin_a: float = 0.0
    status: VerificationCheckStatus = VerificationCheckStatus.PASS
    provenance: ProvenanceCategory = ProvenanceCategory.DERIVED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bus_type": self.bus_type.value,
            "bus_name": self.bus_name,
            "nominal_voltage_v": round(self.nominal_voltage_v, 2),
            "voltage_min_v": round(self.voltage_min_v, 2),
            "voltage_max_v": round(self.voltage_max_v, 2),
            "max_continuous_current_capacity_a": round(self.max_continuous_current_capacity_a, 2),
            "max_peak_current_capacity_a": round(self.max_peak_current_capacity_a, 2),
            "regulator_model": self.regulator_model,
            "source_bus": self.source_bus.value if self.source_bus else None,
            "load_count": len(self.loads),
            "loads": [ld.to_dict() for ld in self.loads],
            "total_continuous_current_a": round(self.total_continuous_current_a, 2),
            "total_peak_current_a": round(self.total_peak_current_a, 2),
            "continuous_margin_a": round(self.continuous_margin_a, 2),
            "peak_margin_a": round(self.peak_margin_a, 2),
            "status": self.status.value,
            "provenance": self.provenance.value,
        }


@dataclass(slots=True)
class PowerPath:
    """An explicit branch in the power tree with verification metrics (Prompt Section 6 & 7)."""
    path_id: str
    path_name: str
    source: str
    destination: str
    voltage_nominal_v: float
    voltage_compatibility: VerificationCheckStatus
    continuous_current_a: float
    peak_current_a: float
    continuous_capacity_a: float
    peak_capacity_a: float
    margin_a: float
    connector_type: str
    regulator_capacity_w: Optional[float]
    status: VerificationCheckStatus
    provenance: ProvenanceCategory
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path_id,
            "path_name": self.path_name,
            "source": self.source,
            "destination": self.destination,
            "voltage_nominal_v": round(self.voltage_nominal_v, 2),
            "voltage_compatibility": self.voltage_compatibility.value,
            "continuous_current_a": round(self.continuous_current_a, 2),
            "peak_current_a": round(self.peak_current_a, 2),
            "continuous_capacity_a": round(self.continuous_capacity_a, 2),
            "peak_capacity_a": round(self.peak_capacity_a, 2),
            "margin_a": round(self.margin_a, 2),
            "connector_type": self.connector_type,
            "regulator_capacity_w": round(self.regulator_capacity_w, 2) if self.regulator_capacity_w is not None else None,
            "status": self.status.value,
            "provenance": self.provenance.value,
            "notes": self.notes,
        }


# =========================================================================
# 3. I/O ALLOCATION MODEL
# =========================================================================

@dataclass(slots=True)
class IOAssignment:
    """
    Deterministic Pixhawk I/O port allocation (Prompt Section 8).
    """
    channel_or_port: str  # e.g., "OUTPUT_1", "TELEM1", "GPS1", "I2C1"
    port_type: IOPortType
    device_role: AircraftRole
    device_name: str
    protocol: SignalProtocol
    direction: str        # "OUTPUT", "INPUT", "BIDIRECTIONAL"
    power_bus: BusType
    baud_rate_or_frequency: Optional[str]
    provenance: ProvenanceCategory
    status: VerificationCheckStatus = VerificationCheckStatus.PASS
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel_or_port": self.channel_or_port,
            "port_type": self.port_type.value,
            "device_role": self.device_role.value,
            "device_name": self.device_name,
            "protocol": self.protocol.value,
            "direction": self.direction,
            "power_bus": self.power_bus.value,
            "baud_rate_or_frequency": self.baud_rate_or_frequency,
            "provenance": self.provenance.value,
            "status": self.status.value,
            "notes": self.notes,
        }


# =========================================================================
# 4. PHYSICAL INSTALLATION & CG MODELS
# =========================================================================

@dataclass(slots=True)
class ComponentLocation:
    """
    Physical coordinates of an installed component relative to aircraft datum (Prompt Section 9).
    Datum: Fuselage Nose (x=0.0m, +x aft, +y starboard/right, +z up).
    """
    component_name: str
    role: Optional[AircraftRole]
    mass_kg: float
    x_m: float
    y_m: float
    z_m: float
    mounting_region: MountingRegion
    reference_frame: str = "AIRCRAFT_BODY_NOSE_DATUM"
    installation_status: VerificationCheckStatus = VerificationCheckStatus.PASS
    provenance: ProvenanceCategory = ProvenanceCategory.CONFIGURABLE_ASSUMPTION
    notes: str = ""

    @property
    def moment_x_kg_m(self) -> float:
        return self.mass_kg * self.x_m

    @property
    def moment_y_kg_m(self) -> float:
        return self.mass_kg * self.y_m

    @property
    def moment_z_kg_m(self) -> float:
        return self.mass_kg * self.z_m

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "role": self.role.value if self.role else None,
            "mass_kg": round(self.mass_kg, 4),
            "x_m": round(self.x_m, 4),
            "y_m": round(self.y_m, 4),
            "z_m": round(self.z_m, 4),
            "mounting_region": self.mounting_region.value,
            "reference_frame": self.reference_frame,
            "installation_status": self.installation_status.value,
            "provenance": self.provenance.value,
            "moment_x_kg_m": round(self.moment_x_kg_m, 4),
            "notes": self.notes,
        }


@dataclass(slots=True)
class IntegratedCGResult:
    """
    Installed Center of Gravity evaluation compared to Phase 6 stability limits (Prompt Section 10).
    """
    total_integrated_mass_kg: float
    x_cg_m: float
    y_cg_m: float
    z_cg_m: float
    x_lemac_m: float
    mac_m: float
    cg_pct_mac: float
    forward_limit_m: float
    aft_limit_m: float
    forward_margin_m: float
    aft_margin_m: float
    static_margin_pct_mac: float
    neutral_point_m: float
    is_within_envelope: bool
    status: VerificationCheckStatus
    provenance: ProvenanceCategory = ProvenanceCategory.DERIVED
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_integrated_mass_kg": round(self.total_integrated_mass_kg, 4),
            "x_cg_m": round(self.x_cg_m, 4),
            "y_cg_m": round(self.y_cg_m, 4),
            "z_cg_m": round(self.z_cg_m, 4),
            "x_lemac_m": round(self.x_lemac_m, 4),
            "mac_m": round(self.mac_m, 4),
            "cg_pct_mac": round(self.cg_pct_mac, 2),
            "forward_limit_m": round(self.forward_limit_m, 4),
            "aft_limit_m": round(self.aft_limit_m, 4),
            "forward_margin_m": round(self.forward_margin_m, 4),
            "aft_margin_m": round(self.aft_margin_m, 4),
            "static_margin_pct_mac": round(self.static_margin_pct_mac, 2),
            "neutral_point_m": round(self.neutral_point_m, 4),
            "is_within_envelope": self.is_within_envelope,
            "status": self.status.value,
            "provenance": self.provenance.value,
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class MassReconciliationResult:
    """
    Comparison of Phase 5 engineering mass vs Phase 8 commercial BOM vs Phase 9 installed (Prompt Section 11).
    """
    phase5_mtow_kg: float
    phase5_hardware_mass_kg: float
    phase8_bom_mass_kg: float
    phase9_installed_mass_kg: float
    hardware_delta_kg: float
    hardware_delta_pct_mtow: float
    mounting_hardware_mass_kg: float
    wiring_and_connectors_mass_kg: float
    structural_mass_kg: float
    payload_mass_kg: float
    battery_mass_kg: float
    avionics_mass_kg: float
    upstream_reevaluation_required: bool
    reevaluation_threshold_kg: float = 0.150
    reevaluation_threshold_pct: float = 2.0
    status: VerificationCheckStatus = VerificationCheckStatus.PASS
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase5_mtow_kg": round(self.phase5_mtow_kg, 4),
            "phase5_hardware_mass_kg": round(self.phase5_hardware_mass_kg, 4),
            "phase8_bom_mass_kg": round(self.phase8_bom_mass_kg, 4),
            "phase9_installed_mass_kg": round(self.phase9_installed_mass_kg, 4),
            "hardware_delta_kg": round(self.hardware_delta_kg, 4),
            "hardware_delta_pct_mtow": round(self.hardware_delta_pct_mtow, 2),
            "mounting_hardware_mass_kg": round(self.mounting_hardware_mass_kg, 4),
            "wiring_and_connectors_mass_kg": round(self.wiring_and_connectors_mass_kg, 4),
            "structural_mass_kg": round(self.structural_mass_kg, 4),
            "payload_mass_kg": round(self.payload_mass_kg, 4),
            "battery_mass_kg": round(self.battery_mass_kg, 4),
            "avionics_mass_kg": round(self.avionics_mass_kg, 4),
            "upstream_reevaluation_required": self.upstream_reevaluation_required,
            "status": self.status.value,
            "notes": list(self.notes),
        }


# =========================================================================
# 5. MISSION-STATE & TRANSITION INTEGRATION MODELS
# =========================================================================

@dataclass(slots=True)
class StateDeviceStatus:
    """Operational status of a hardware subsystem in a specific mission state."""
    role: AircraftRole
    device_name: str
    is_active: bool
    power_draw_w: float
    interface_active: bool
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "device_name": self.device_name,
            "is_active": self.is_active,
            "power_draw_w": round(self.power_draw_w, 2),
            "interface_active": self.interface_active,
            "notes": self.notes,
        }


@dataclass(slots=True)
class MissionStateIntegrationResult:
    """Hardware readiness and activity state for a single mission phase (Prompt Section 13)."""
    state: MissionState
    active_motors: List[str]
    inactive_motors: List[str]
    active_control_surfaces: List[str]
    active_sensors: List[str]
    active_telemetry: bool
    active_companion_computer: bool
    required_power_buses: List[BusType]
    state_power_draw_w: float
    state_duration_sec: float
    state_dependencies: List[str]
    status: VerificationCheckStatus
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "active_motors": list(self.active_motors),
            "inactive_motors": list(self.inactive_motors),
            "active_control_surfaces": list(self.active_control_surfaces),
            "active_sensors": list(self.active_sensors),
            "active_telemetry": self.active_telemetry,
            "active_companion_computer": self.active_companion_computer,
            "required_power_buses": [b.value for b in self.required_power_buses],
            "state_power_draw_w": round(self.state_power_draw_w, 2),
            "state_duration_sec": round(self.state_duration_sec, 1),
            "state_dependencies": list(self.state_dependencies),
            "status": self.status.value,
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class TransitionIntegrationResult:
    """Hardware readiness for inbound and outbound transition corridors (Prompt Section 14)."""
    vtol_to_cruise_ready: bool
    cruise_to_vtol_ready: bool
    lift_motors_available: bool
    cruise_motor_available: bool
    control_surfaces_available: bool
    airspeed_sensor_available: bool
    nav_attitude_available: bool
    power_headroom_w: float
    abort_reversal_supported: bool
    status: VerificationCheckStatus
    provenance: ProvenanceCategory = ProvenanceCategory.DERIVED
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vtol_to_cruise_ready": self.vtol_to_cruise_ready,
            "cruise_to_vtol_ready": self.cruise_to_vtol_ready,
            "lift_motors_available": self.lift_motors_available,
            "cruise_motor_available": self.cruise_motor_available,
            "control_surfaces_available": self.control_surfaces_available,
            "airspeed_sensor_available": self.airspeed_sensor_available,
            "nav_attitude_available": self.nav_attitude_available,
            "power_headroom_w": round(self.power_headroom_w, 2),
            "abort_reversal_supported": self.abort_reversal_supported,
            "status": self.status.value,
            "provenance": self.provenance.value,
            "notes": list(self.notes),
        }


# =========================================================================
# 6. FAILURE-MODE ANALYSIS (FMEA) MODEL
# =========================================================================

@dataclass(slots=True)
class FailureModeResult:
    """Record of an integrated system failure mode evaluation (Prompt Section 15)."""
    failure_id: str
    failure_mode: str
    affected_subsystem: str
    mission_states_affected: List[MissionState]
    severity: str  # "CRITICAL", "MAJOR", "MINOR"
    existing_mitigation: str
    required_autopilot_response: str
    controllability_status: ControllabilityStatus
    verification_status: VerificationCheckStatus
    provenance: ProvenanceCategory
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "failure_mode": self.failure_mode,
            "affected_subsystem": self.affected_subsystem,
            "mission_states_affected": [s.value for s in self.mission_states_affected],
            "severity": self.severity,
            "existing_mitigation": self.existing_mitigation,
            "required_autopilot_response": self.required_autopilot_response,
            "controllability_status": self.controllability_status.value,
            "verification_status": self.verification_status.value,
            "provenance": self.provenance.value,
            "notes": self.notes,
        }


# =========================================================================
# 7. INTERFACE INVENTORY & THERMAL MODELS
# =========================================================================

@dataclass(slots=True)
class ConnectorInterfaceItem:
    """Record in the connector/cable interface inventory (Prompt Section 16)."""
    interface_id: str
    source_device: str
    destination_device: str
    signal_or_power: str
    connector_type: str  # XT90, XT60, JST-GH, MR30, Molex, DEFERRED
    wire_gauge_awg: Optional[str]
    selection_status: VerificationCheckStatus
    provenance: ProvenanceCategory
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interface_id": self.interface_id,
            "source_device": self.source_device,
            "destination_device": self.destination_device,
            "signal_or_power": self.signal_or_power,
            "connector_type": self.connector_type,
            "wire_gauge_awg": self.wire_gauge_awg,
            "selection_status": self.selection_status.value,
            "provenance": self.provenance.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class ThermalCheckItem:
    """Thermal dissipation check for high-current components (Prompt Section 17)."""
    component_name: str
    heat_dissipation_est_w: float
    max_operating_temp_c: Optional[float]
    cooling_mechanism: str
    cfd_model_status: VerificationCheckStatus  # DEFERRED
    check_status: VerificationCheckStatus
    provenance: ProvenanceCategory
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "heat_dissipation_est_w": round(self.heat_dissipation_est_w, 2),
            "max_operating_temp_c": self.max_operating_temp_c,
            "cooling_mechanism": self.cooling_mechanism,
            "cfd_model_status": self.cfd_model_status.value,
            "check_status": self.check_status.value,
            "provenance": self.provenance.value,
            "notes": self.notes,
        }


# =========================================================================
# 8. REQUIREMENT TRACEABILITY MODEL
# =========================================================================

@dataclass(slots=True)
class IntegrationRequirementTrace:
    """Traceability record linking upstream requirements to integrated verification (Prompt Section 18)."""
    requirement_id: str
    parameter: str
    source_phase: int
    upstream_value: str
    selected_hardware: str
    integration_result: str
    evidence: str
    provenance: ProvenanceCategory
    status: VerificationCheckStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "parameter": self.parameter,
            "source_phase": self.source_phase,
            "upstream_value": self.upstream_value,
            "selected_hardware": self.selected_hardware,
            "integration_result": self.integration_result,
            "evidence": self.evidence,
            "provenance": self.provenance.value,
            "status": self.status.value,
        }


# =========================================================================
# 9. INTEGRATION VERIFICATION & PIPELINE RESULT MODELS
# =========================================================================

@dataclass(slots=True)
class IntegrationVerificationResult:
    """Consolidated verification report across all integration domains."""
    hardware_assignment_passed: bool
    electrical_architecture_passed: bool
    io_allocation_passed: bool
    physical_installation_passed: bool
    cg_envelope_passed: bool
    mass_reconciliation_passed: bool
    mission_states_passed: bool
    transition_integration_passed: bool
    failure_analysis_passed: bool
    thermal_checks_passed: bool
    has_critical_failure: bool
    has_warnings: bool
    total_checks_count: int
    passed_checks_count: int
    warning_checks_count: int
    deferred_checks_count: int
    failed_checks_count: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hardware_assignment_passed": self.hardware_assignment_passed,
            "electrical_architecture_passed": self.electrical_architecture_passed,
            "io_allocation_passed": self.io_allocation_passed,
            "physical_installation_passed": self.physical_installation_passed,
            "cg_envelope_passed": self.cg_envelope_passed,
            "mass_reconciliation_passed": self.mass_reconciliation_passed,
            "mission_states_passed": self.mission_states_passed,
            "transition_integration_passed": self.transition_integration_passed,
            "failure_analysis_passed": self.failure_analysis_passed,
            "thermal_checks_passed": self.thermal_checks_passed,
            "has_critical_failure": self.has_critical_failure,
            "has_warnings": self.has_warnings,
            "total_checks_count": self.total_checks_count,
            "passed_checks_count": self.passed_checks_count,
            "warning_checks_count": self.warning_checks_count,
            "deferred_checks_count": self.deferred_checks_count,
            "failed_checks_count": self.failed_checks_count,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(slots=True)
class IntegrationConfiguration:
    """Input configuration parameters for the Phase 9 integration engine."""
    enable_detailed_cg: bool = True
    allow_assumptions_for_connectors: bool = True
    reevaluation_mass_threshold_kg: float = 0.150
    reevaluation_mass_threshold_pct: float = 2.0
    servo_torque_qualification: str = "DEFERRED_INSUFFICIENT_INPUT"
    thermal_cfd_qualification: str = "DEFERRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enable_detailed_cg": self.enable_detailed_cg,
            "allow_assumptions_for_connectors": self.allow_assumptions_for_connectors,
            "reevaluation_mass_threshold_kg": self.reevaluation_mass_threshold_kg,
            "reevaluation_mass_threshold_pct": self.reevaluation_mass_threshold_pct,
            "servo_torque_qualification": self.servo_torque_qualification,
            "thermal_cfd_qualification": self.thermal_cfd_qualification,
        }


@dataclass(slots=True)
class IntegrationPipelineResult:
    """
    Master authoritative output of Phase 9 System Integration and Verification pipeline.
    """
    final_status: IntegrationStatus
    assignments: List[HardwareAssignment]
    electrical_buses: List[ElectricalBus]
    power_paths: List[PowerPath]
    io_allocations: List[IOAssignment]
    installed_components: List[ComponentLocation]
    integrated_cg: IntegratedCGResult
    mass_reconciliation: MassReconciliationResult
    mission_states: List[MissionStateIntegrationResult]
    transition_integration: TransitionIntegrationResult
    failure_modes: List[FailureModeResult]
    connectors: List[ConnectorInterfaceItem]
    thermal_checks: List[ThermalCheckItem]
    traceability_table: List[IntegrationRequirementTrace]
    verification: IntegrationVerificationResult
    configuration: IntegrationConfiguration
    deferred_items: List[str] = field(default_factory=list)
    insufficient_input_items: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "final_status": self.final_status.value,
            "assignments_count": len(self.assignments),
            "assignments": [a.to_dict() for a in self.assignments],
            "electrical_buses_count": len(self.electrical_buses),
            "electrical_buses": [b.to_dict() for b in self.electrical_buses],
            "power_paths_count": len(self.power_paths),
            "power_paths": [p.to_dict() for p in self.power_paths],
            "io_allocations_count": len(self.io_allocations),
            "io_allocations": [io.to_dict() for io in self.io_allocations],
            "installed_components_count": len(self.installed_components),
            "installed_components": [c.to_dict() for c in self.installed_components],
            "integrated_cg": self.integrated_cg.to_dict(),
            "mass_reconciliation": self.mass_reconciliation.to_dict(),
            "mission_states_count": len(self.mission_states),
            "mission_states": [ms.to_dict() for ms in self.mission_states],
            "transition_integration": self.transition_integration.to_dict(),
            "failure_modes_count": len(self.failure_modes),
            "failure_modes": [fm.to_dict() for fm in self.failure_modes],
            "connectors_count": len(self.connectors),
            "connectors": [c.to_dict() for c in self.connectors],
            "thermal_checks_count": len(self.thermal_checks),
            "thermal_checks": [th.to_dict() for th in self.thermal_checks],
            "traceability_count": len(self.traceability_table),
            "traceability_table": [tr.to_dict() for tr in self.traceability_table],
            "verification": self.verification.to_dict(),
            "configuration": self.configuration.to_dict(),
            "deferred_items": list(self.deferred_items),
            "insufficient_input_items": list(self.insufficient_input_items),
            "metadata": dict(self.metadata),
        }
