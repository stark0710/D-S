"""
VTOL Phase 11 Domain Models: Physical Ground Verification & Pixhawk Commissioning.

Defines typed dataclasses, domain enums, and recursive serialization for
bench-level physical verification, power commissioning, sensor validation,
actuator mapping, failsafe verification, defect tracking, and ground test evidence.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GroundTestStatus(str, Enum):
    """Execution status for individual ground test procedures."""
    NOT_EXECUTED = "NOT_EXECUTED"
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    DEFERRED = "DEFERRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    FLIGHT_TEST_REQUIRED = "FLIGHT_TEST_REQUIRED"


class GroundVerificationVerdict(str, Enum):
    """Overall Phase 11 commissioning verdict."""
    GROUND_VERIFICATION_NOT_EXECUTED = "GROUND_VERIFICATION_NOT_EXECUTED"
    GROUND_VERIFICATION_COMPLETE = "GROUND_VERIFICATION_COMPLETE"
    GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS = "GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS"
    GROUND_VERIFICATION_BLOCKED = "GROUND_VERIFICATION_BLOCKED"


class DefectSeverity(str, Enum):
    """Severity classification for physical ground test defects."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class DefectStatus(str, Enum):
    """Lifecycle status of an identified defect."""
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    INVESTIGATING = "INVESTIGATING"
    ACCEPTED_LIMITATION = "ACCEPTED_LIMITATION"


class CalibrationStatus(str, Enum):
    """Sensor physical calibration status."""
    NOT_CALIBRATED = "NOT_CALIBRATED"
    CALIBRATION_COMPLETED = "CALIBRATION_COMPLETED"
    CALIBRATION_FAILED = "CALIBRATION_FAILED"
    CALIBRATION_DEFERRED = "CALIBRATION_DEFERRED"


class InspectionStatus(str, Enum):
    """Power-off visual/electrical inspection status."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_EXECUTED = "NOT_EXECUTED"


class HardwareReconciliationStatus(str, Enum):
    """Status of physical hardware verification against authorized BOM."""
    HARDWARE_MATCH_CONFIRMED = "HARDWARE_MATCH_CONFIRMED"
    HARDWARE_IDENTITY_CONFLICT = "HARDWARE_IDENTITY_CONFLICT"
    ACTUAL_HARDWARE_DIFFERS_FROM_AUTHORIZED_BOM = "ACTUAL_HARDWARE_DIFFERS_FROM_AUTHORIZED_BOM"


@dataclass(slots=True)
class PhysicalComponent:
    """A physical component installed on the aircraft under test."""
    component_id: str
    name: str
    manufacturer: str
    model: str
    serial_number: str
    quantity: int
    physical_location: str
    electrical_connection: str
    software_identity: str
    bom_identity: str
    phase10_identity: str
    verification_status: HardwareReconciliationStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serial_number": self.serial_number,
            "quantity": self.quantity,
            "physical_location": self.physical_location,
            "electrical_connection": self.electrical_connection,
            "software_identity": self.software_identity,
            "bom_identity": self.bom_identity,
            "phase10_identity": self.phase10_identity,
            "verification_status": self.verification_status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class ElectricalInspectionItem:
    """A single power-off electrical inspection check."""
    check_id: str
    title: str
    test_point: str
    status: InspectionStatus
    expected_condition: str
    observed_condition: str
    safety_critical: bool = True
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "test_point": self.test_point,
            "status": self.status.value,
            "expected_condition": self.expected_condition,
            "observed_condition": self.observed_condition,
            "safety_critical": self.safety_critical,
            "notes": self.notes,
        }


@dataclass(slots=True)
class PowerRailMeasurement:
    """Voltage measurement on a specific power distribution rail."""
    rail_name: str
    nominal_voltage_v: float
    min_voltage_v: float
    max_voltage_v: float
    measured_voltage_v: Optional[float]
    instrument: str
    test_condition: str
    status: InspectionStatus
    notes: str = ""

    @property
    def difference_v(self) -> Optional[float]:
        if self.measured_voltage_v is None:
            return None
        return round(self.measured_voltage_v - self.nominal_voltage_v, 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rail_name": self.rail_name,
            "nominal_voltage_v": self.nominal_voltage_v,
            "min_voltage_v": self.min_voltage_v,
            "max_voltage_v": self.max_voltage_v,
            "measured_voltage_v": self.measured_voltage_v,
            "difference_v": self.difference_v,
            "instrument": self.instrument,
            "test_condition": self.test_condition,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class PixhawkCommissioningRecord:
    """Pixhawk 6X hardware and firmware commissioning state."""
    flight_controller: str
    board_id: str
    firmware_version: str
    parameter_checksum: str
    parameter_load_status: GroundTestStatus
    sensor_bus_enumeration: GroundTestStatus
    sd_card_logging_status: GroundTestStatus
    usb_telemetry_status: GroundTestStatus
    arming_prerequisites_status: GroundTestStatus
    safety_switch_operational: bool
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flight_controller": self.flight_controller,
            "board_id": self.board_id,
            "firmware_version": self.firmware_version,
            "parameter_checksum": self.parameter_checksum,
            "parameter_load_status": self.parameter_load_status.value,
            "sensor_bus_enumeration": self.sensor_bus_enumeration.value,
            "sd_card_logging_status": self.sd_card_logging_status.value,
            "usb_telemetry_status": self.usb_telemetry_status.value,
            "arming_prerequisites_status": self.arming_prerequisites_status.value,
            "safety_switch_operational": self.safety_switch_operational,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class SensorVerificationRecord:
    """Verification state for a specific sensor subsystem."""
    sensor_name: str
    hardware_model: str
    interface_bus: str
    detected: bool
    configured: bool
    calibration_status: CalibrationStatus
    reading_sample: str
    expected_range: str
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_name": self.sensor_name,
            "hardware_model": self.hardware_model,
            "interface_bus": self.interface_bus,
            "detected": self.detected,
            "configured": self.configured,
            "calibration_status": self.calibration_status.value,
            "reading_sample": self.reading_sample,
            "expected_range": self.expected_range,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class OutputVerificationRecord:
    """Actuator output channel physical mapping verification."""
    output_channel: int
    commanded_actuator: str
    observed_actuator: str
    protocol: str
    signal_range: str
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_channel": self.output_channel,
            "commanded_actuator": self.commanded_actuator,
            "observed_actuator": self.observed_actuator,
            "protocol": self.protocol,
            "signal_range": self.signal_range,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class MotorIdentificationRecord:
    """Motor physical verification record (propellers removed)."""
    motor_id: str
    physical_position: str
    output_channel: int
    esc_model: str
    propeller_removed: bool
    commanded_sequence: int
    observed_sequence: int
    required_direction: str
    observed_direction: str
    start_behavior: str
    abnormal_vibration: bool
    abnormal_sound: bool
    direction_status: GroundTestStatus
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "motor_id": self.motor_id,
            "physical_position": self.physical_position,
            "output_channel": self.output_channel,
            "esc_model": self.esc_model,
            "propeller_removed": self.propeller_removed,
            "commanded_sequence": self.commanded_sequence,
            "observed_sequence": self.observed_sequence,
            "required_direction": self.required_direction,
            "observed_direction": self.observed_direction,
            "start_behavior": self.start_behavior,
            "abnormal_vibration": self.abnormal_vibration,
            "abnormal_sound": self.abnormal_sound,
            "direction_status": self.direction_status.value,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class ServoVerificationRecord:
    """Flight control surface servo bench verification."""
    surface_name: str
    output_channel: int
    servo_model: str
    neutral_pwm: int
    min_pwm: int
    max_pwm: int
    commanded_movement: str
    observed_movement: str
    aerodynamic_direction_correct: bool
    travel_deg: float
    mechanical_binding: bool
    abnormal_noise: bool
    direction_status: GroundTestStatus
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_name": self.surface_name,
            "output_channel": self.output_channel,
            "servo_model": self.servo_model,
            "neutral_pwm": self.neutral_pwm,
            "min_pwm": self.min_pwm,
            "max_pwm": self.max_pwm,
            "commanded_movement": self.commanded_movement,
            "observed_movement": self.observed_movement,
            "aerodynamic_direction_correct": self.aerodynamic_direction_correct,
            "travel_deg": self.travel_deg,
            "mechanical_binding": self.mechanical_binding,
            "abnormal_noise": self.abnormal_noise,
            "direction_status": self.direction_status.value,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class VTailVerificationRecord:
    """Inverted V-tail elevator and rudder differential mixing verification."""
    test_condition: str
    stick_command: str
    left_ruddervator_observed: str
    right_ruddervator_observed: str
    expected_aerodynamic_moment: str
    mathematical_mixing_model: str
    physical_sign_inversion: bool
    mixing_correct: bool
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_condition": self.test_condition,
            "stick_command": self.stick_command,
            "left_ruddervator_observed": self.left_ruddervator_observed,
            "right_ruddervator_observed": self.right_ruddervator_observed,
            "expected_aerodynamic_moment": self.expected_aerodynamic_moment,
            "mathematical_mixing_model": self.mathematical_mixing_model,
            "physical_sign_inversion": self.physical_sign_inversion,
            "mixing_correct": self.mixing_correct,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class FailsafeTestRecord:
    """Bench-level failsafe injection test."""
    failsafe_id: str
    trigger: str
    expected_response: str
    observed_response: str
    response_time_s: Optional[float]
    safe_disarm_verified: bool
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failsafe_id": self.failsafe_id,
            "trigger": self.trigger,
            "expected_response": self.expected_response,
            "observed_response": self.observed_response,
            "response_time_s": self.response_time_s,
            "safe_disarm_verified": self.safe_disarm_verified,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class TransitionBenchRecord:
    """Bench verification of ArduPilot QuadPlane transition logic (props removed)."""
    trigger_airspeed_m_s: float
    pusher_throttle_observed: str
    transition_timer_duration_s: float
    vtol_motor_shutdown_observed: bool
    abort_reversal_command_tested: bool
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_airspeed_m_s": self.trigger_airspeed_m_s,
            "pusher_throttle_observed": self.pusher_throttle_observed,
            "transition_timer_duration_s": self.transition_timer_duration_s,
            "vtol_motor_shutdown_observed": self.vtol_motor_shutdown_observed,
            "abort_reversal_command_tested": self.abort_reversal_command_tested,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class ThermalCheckRecord:
    """Bench component thermal observation under sustained idle/spool."""
    component_name: str
    test_duration_s: float
    ambient_temp_c: float
    measured_temp_c: Optional[float]
    measurement_method: str
    within_limits: bool
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "test_duration_s": self.test_duration_s,
            "ambient_temp_c": self.ambient_temp_c,
            "measured_temp_c": self.measured_temp_c,
            "measurement_method": self.measurement_method,
            "within_limits": self.within_limits,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class MassCGMeasurementRecord:
    """Physical mass and Center of Gravity reconciliation check."""
    measured_total_mass_kg: Optional[float]
    phase5_predicted_mass_kg: float
    mass_delta_kg: Optional[float]
    measured_cg_x_m: Optional[float]
    phase9_installed_cg_x_m: float
    cg_delta_m: Optional[float]
    reconciliation_required: bool
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "measured_total_mass_kg": self.measured_total_mass_kg,
            "phase5_predicted_mass_kg": self.phase5_predicted_mass_kg,
            "mass_delta_kg": self.mass_delta_kg,
            "measured_cg_x_m": self.measured_cg_x_m,
            "phase9_installed_cg_x_m": self.phase9_installed_cg_x_m,
            "cg_delta_m": self.cg_delta_m,
            "reconciliation_required": self.reconciliation_required,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class GroundTestEvidenceRecord:
    """Forensic evidence container for one of the 18 ground procedures."""
    test_id: str
    test_name: str
    date: str
    operator: str
    configuration_version: str
    hardware_tested: str
    procedure_summary: str
    expected_result: str
    observed_result: str
    measurement: str
    instrument: str
    log_reference: str
    status: GroundTestStatus
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "date": self.date,
            "operator": self.operator,
            "configuration_version": self.configuration_version,
            "hardware_tested": self.hardware_tested,
            "procedure_summary": self.procedure_summary,
            "expected_result": self.expected_result,
            "observed_result": self.observed_result,
            "measurement": self.measurement,
            "instrument": self.instrument,
            "log_reference": self.log_reference,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class DefectRecord:
    """Structured defect record discovered during physical ground verification."""
    defect_id: str
    severity: DefectSeverity
    test_id: str
    description: str
    expected: str
    observed: str
    root_cause_status: str
    affected_subsystem: str
    upstream_phase: str
    recommended_action: str
    status: DefectStatus = DefectStatus.OPEN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "defect_id": self.defect_id,
            "severity": self.severity.value,
            "test_id": self.test_id,
            "description": self.description,
            "expected": self.expected,
            "observed": self.observed,
            "root_cause_status": self.root_cause_status,
            "affected_subsystem": self.affected_subsystem,
            "upstream_phase": self.upstream_phase,
            "recommended_action": self.recommended_action,
            "status": self.status.value,
        }


@dataclass(slots=True)
class UpstreamReconciliationRecord:
    """Tracked parameter deviation requiring upstream review."""
    parameter_name: str
    measured_result: str
    engineering_assumption: str
    delta: str
    impact: str
    required_upstream_review: str
    status: str = "RECORDED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "measured_result": self.measured_result,
            "engineering_assumption": self.engineering_assumption,
            "delta": self.delta,
            "impact": self.impact,
            "required_upstream_review": self.required_upstream_review,
            "status": self.status,
        }


@dataclass(slots=True)
class GroundVerificationState:
    """Master aggregate representing the full Phase 11 commissioning state."""
    aircraft_name: str
    configuration_version: str
    pixhawk_commissioning: PixhawkCommissioningRecord
    physical_inventory: List[PhysicalComponent]
    electrical_inspection: List[ElectricalInspectionItem]
    power_rail_measurements: List[PowerRailMeasurement]
    sensor_verifications: List[SensorVerificationRecord]
    output_verifications: List[OutputVerificationRecord]
    motor_identifications: List[MotorIdentificationRecord]
    servo_verifications: List[ServoVerificationRecord]
    vtail_verification: VTailVerificationRecord
    failsafe_tests: List[FailsafeTestRecord]
    transition_bench: TransitionBenchRecord
    thermal_checks: List[ThermalCheckRecord]
    mass_cg_measurement: MassCGMeasurementRecord
    ground_tests: List[GroundTestEvidenceRecord]
    defects: List[DefectRecord]
    upstream_reconciliations: List[UpstreamReconciliationRecord]
    hardware_reconciliation_verdict: HardwareReconciliationStatus
    verdict: GroundVerificationVerdict
    verdict_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aircraft_name": self.aircraft_name,
            "configuration_version": self.configuration_version,
            "pixhawk_commissioning": self.pixhawk_commissioning.to_dict(),
            "physical_inventory": [c.to_dict() for c in self.physical_inventory],
            "electrical_inspection": [e.to_dict() for e in self.electrical_inspection],
            "power_rail_measurements": [p.to_dict() for p in self.power_rail_measurements],
            "sensor_verifications": [s.to_dict() for s in self.sensor_verifications],
            "output_verifications": [o.to_dict() for o in self.output_verifications],
            "motor_identifications": [m.to_dict() for m in self.motor_identifications],
            "servo_verifications": [sv.to_dict() for sv in self.servo_verifications],
            "vtail_verification": self.vtail_verification.to_dict(),
            "failsafe_tests": [f.to_dict() for f in self.failsafe_tests],
            "transition_bench": self.transition_bench.to_dict(),
            "thermal_checks": [t.to_dict() for t in self.thermal_checks],
            "mass_cg_measurement": self.mass_cg_measurement.to_dict(),
            "ground_tests": [gt.to_dict() for gt in self.ground_tests],
            "defects": [d.to_dict() for d in self.defects],
            "upstream_reconciliations": [u.to_dict() for u in self.upstream_reconciliations],
            "hardware_reconciliation_verdict": self.hardware_reconciliation_verdict.value,
            "verdict": self.verdict.value,
            "verdict_explanation": self.verdict_explanation,
        }
