"""
VTOL Phase 10 Flight-Control Configuration & ArduPilot Integration — Domain Models.

Purpose:
    Typed dataclasses defining ArduPilot QuadPlane parameters, actuator and motor
    output mappings, servo kinematics, inverted V-tail mixing, sensor drivers,
    failsafe scenarios, pre-flight safety gates, ground-test procedures,
    and hardware identity reconciliation.

Standards:
    - Downstream of Phases 1-9: strictly consumes authoritative outputs without mutation.
    - Explicit parameter provenance tracking with confidence ratings.
    - Zero fabrication: unverified physical directions marked UNVERIFIED_REQUIRES_BENCH_TEST;
      untested software responses marked CONFIGURATION_SUPPORTED;
      hardware mismatches flagged as HARDWARE_IDENTITY_CONFLICT.
    - 100% recursive JSON serialization across all dataclasses.
"""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FlightControlStatus(str, Enum):
    """Explicit verification and execution statuses (Prompt Section 33)."""
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    GROUND_TEST_REQUIRED = "GROUND_TEST_REQUIRED"
    FLIGHT_TEST_REQUIRED = "FLIGHT_TEST_REQUIRED"
    DEFERRED = "DEFERRED"
    CONFIGURABLE_ASSUMPTION = "CONFIGURABLE_ASSUMPTION"
    HARDWARE_IDENTITY_CONFLICT = "HARDWARE_IDENTITY_CONFLICT"
    UPSTREAM_CHANGE_REQUIRED = "UPSTREAM_CHANGE_REQUIRED"


class FinalVerdictStatus(str, Enum):
    """Final Phase 10 integration verdict states (Prompt Section 34)."""
    FLIGHT_CONTROL_CONFIGURATION_COMPLETE = "FLIGHT_CONTROL_CONFIGURATION_COMPLETE"
    FLIGHT_CONTROL_CONFIGURATION_COMPLETE_WITH_WARNINGS = "FLIGHT_CONTROL_CONFIGURATION_COMPLETE_WITH_WARNINGS"
    FLIGHT_CONTROL_CONFIGURATION_BLOCKED = "FLIGHT_CONTROL_CONFIGURATION_BLOCKED"


class GroundTestReadiness(str, Enum):
    """Hardware ground-test readiness categories (Prompt Section 16 & 30)."""
    READY_FOR_GROUND_TEST = "READY_FOR_GROUND_TEST"
    READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
    BLOCKED = "BLOCKED"
    CONFIGURATION_INCOMPLETE = "CONFIGURATION_INCOMPLETE"


class GroundTestExecutionStatus(str, Enum):
    """Ground-test bench verification execution states (Prompt Section 25)."""
    NOT_EXECUTED = "NOT_EXECUTED"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class OutputProtocol(str, Enum):
    """Actuator electrical and digital signaling protocols (Prompt Section 7)."""
    DSHOT600 = "DSHOT600"
    DSHOT300 = "DSHOT300"
    DSHOT150 = "DSHOT150"
    FAST_PWM_400HZ = "FAST_PWM_400HZ"
    STANDARD_PWM_50HZ = "STANDARD_PWM_50HZ"
    DIGITAL_PWM_333HZ = "DIGITAL_PWM_333HZ"
    DISCRETE_GPIO = "DISCRETE_GPIO"
    CONFIGURATION_PENDING = "CONFIGURATION_PENDING"


class MotorRotationDirection(str, Enum):
    """Physical rotor rotation direction (Prompt Section 6)."""
    CW = "CW"
    CCW = "CCW"
    UNVERIFIED_REQUIRES_BENCH_TEST = "UNVERIFIED_REQUIRES_BENCH_TEST"


class ParameterSourceType(str, Enum):
    """Strict parameter source taxonomy (Prompt Section 22)."""
    PROJECT_REQUIREMENT = "PROJECT_REQUIREMENT"
    PHASE_1_OUTPUT = "PHASE_1_OUTPUT"
    PHASE_2_OUTPUT = "PHASE_2_OUTPUT"
    PHASE_3_OUTPUT = "PHASE_3_OUTPUT"
    PHASE_4_OUTPUT = "PHASE_4_OUTPUT"
    PHASE_5_OUTPUT = "PHASE_5_OUTPUT"
    PHASE_6_OUTPUT = "PHASE_6_OUTPUT"
    PHASE_7_OUTPUT = "PHASE_7_OUTPUT"
    PHASE_8_HARDWARE = "PHASE_8_HARDWARE"
    PHASE_9_INTEGRATION = "PHASE_9_INTEGRATION"
    ARDUPILOT_DOCUMENTATION = "ARDUPILOT_DOCUMENTATION"
    ARDUPILOT_SOURCE = "ARDUPILOT_SOURCE"
    HARDWARE_DATASHEET = "HARDWARE_DATASHEET"
    CONFIGURABLE_ASSUMPTION = "CONFIGURABLE_ASSUMPTION"
    DEFERRED = "DEFERRED"
    UNKNOWN = "UNKNOWN"


class ParameterConfidence(str, Enum):
    """Degree of empirical or analytical certainty for a parameter."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNTESTED = "UNTESTED"


class FailsafeResponseAction(str, Enum):
    """Configured autopilot safety response."""
    RTL = "RTL"
    QRTL = "QRTL"
    QHOVER = "QHOVER"
    QLAND = "QLAND"
    FBWA = "FBWA"
    GLIDE_DESCENT = "GLIDE_DESCENT"
    CONTINUE_MISSION = "CONTINUE_MISSION"
    TERMINATION_PARACHUTE = "TERMINATION_PARACHUTE"
    IOMCU_FAILOVER = "IOMCU_FAILOVER"
    WARN_ONLY = "WARN_ONLY"


@dataclass
class ArduPilotParameter:
    """Individual ArduPilot parameter specification with strict provenance (Prompt Section 8 & 22)."""
    parameter_name: str
    value: float | int | str
    unit: str
    purpose: str
    source: str
    source_type: ParameterSourceType
    required_or_optional: str = "REQUIRED"
    confidence: ParameterConfidence = ParameterConfidence.HIGH
    status: FlightControlStatus = FlightControlStatus.PASS
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "value": self.value,
            "unit": self.unit,
            "purpose": self.purpose,
            "source": self.source,
            "source_type": self.source_type.value,
            "required_or_optional": self.required_or_optional,
            "confidence": self.confidence.value,
            "status": self.status.value,
            "notes": self.notes,
        }


@dataclass
class MotorOutputAssignment:
    """Actuator mapping for propulsion motors (Prompt Section 6)."""
    motor_id: str
    physical_position: str
    output_channel: int  # PWM channel 1-16
    assigned_role: str
    hardware_esc: str
    hardware_motor: str
    hardware_propeller: str
    protocol: OutputProtocol
    signal_frequency_hz: Optional[float]
    nominal_rotation_direction: MotorRotationDirection
    direction_verification_status: FlightControlStatus
    failsafe_action: str
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "motor_id": self.motor_id,
            "physical_position": self.physical_position,
            "output_channel": self.output_channel,
            "assigned_role": self.assigned_role,
            "hardware_esc": self.hardware_esc,
            "hardware_motor": self.hardware_motor,
            "hardware_propeller": self.hardware_propeller,
            "protocol": self.protocol.value,
            "signal_frequency_hz": self.signal_frequency_hz,
            "nominal_rotation_direction": self.nominal_rotation_direction.value,
            "direction_verification_status": self.direction_verification_status.value,
            "failsafe_action": self.failsafe_action,
            "notes": self.notes,
        }


@dataclass
class ServoOutputAssignment:
    """Actuator mapping and kinematic limits for aerodynamic surfaces (Prompt Section 14)."""
    surface_name: str
    output_channel: int
    servo_function_param: str
    servo_function_id: int
    hardware_servo: str
    pwm_min_us: int
    pwm_neutral_us: int
    pwm_max_us: int
    pwm_trim_us: int
    protocol: OutputProtocol
    signal_frequency_hz: float
    direction_reversed: bool
    direction_verification_status: FlightControlStatus
    hinge_torque_status: FlightControlStatus
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_name": self.surface_name,
            "output_channel": self.output_channel,
            "servo_function_param": self.servo_function_param,
            "servo_function_id": self.servo_function_id,
            "hardware_servo": self.hardware_servo,
            "pwm_min_us": self.pwm_min_us,
            "pwm_neutral_us": self.pwm_neutral_us,
            "pwm_max_us": self.pwm_max_us,
            "pwm_trim_us": self.pwm_trim_us,
            "protocol": self.protocol.value,
            "signal_frequency_hz": self.signal_frequency_hz,
            "direction_reversed": self.direction_reversed,
            "direction_verification_status": self.direction_verification_status.value,
            "hinge_torque_status": self.hinge_torque_status.value,
            "notes": self.notes,
        }


@dataclass
class VTailMixerConfiguration:
    """Mathematical inverted V-tail mixer configuration (Prompt Section 15)."""
    aircraft_tail_configuration: str = "INVERTED_V_TAIL"
    left_surface_equation: str = "LeftSurface = ElevatorComponent + RudderComponent"
    right_surface_equation: str = "RightSurface = ElevatorComponent - RudderComponent"
    mixer_type_param: str = "MIXING_OFFSET / V_TAIL"
    mixing_model_status: FlightControlStatus = FlightControlStatus.PASS
    physical_direction_status: FlightControlStatus = FlightControlStatus.GROUND_TEST_REQUIRED
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aircraft_tail_configuration": self.aircraft_tail_configuration,
            "left_surface_equation": self.left_surface_equation,
            "right_surface_equation": self.right_surface_equation,
            "mixer_type_param": self.mixer_type_param,
            "mixing_model_status": self.mixing_model_status.value,
            "physical_direction_status": self.physical_direction_status.value,
            "notes": self.notes,
        }


@dataclass
class SensorConfigurationItem:
    """Sensor interface and driver setup (Prompt Section 12)."""
    sensor_name: str
    hardware_component: str
    bus_interface: str
    protocol: str
    ardupilot_driver_param: str
    driver_param_value: int | str
    calibration_requirement: str
    redundancy_support: str
    failure_detection_method: str
    failsafe_response: str
    configuration_status: FlightControlStatus
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_name": self.sensor_name,
            "hardware_component": self.hardware_component,
            "bus_interface": self.bus_interface,
            "protocol": self.protocol,
            "ardupilot_driver_param": self.ardupilot_driver_param,
            "driver_param_value": self.driver_param_value,
            "calibration_requirement": self.calibration_requirement,
            "redundancy_support": self.redundancy_support,
            "failure_detection_method": self.failure_detection_method,
            "failsafe_response": self.failsafe_response,
            "configuration_status": self.configuration_status.value,
            "notes": self.notes,
        }


@dataclass
class FlightModeItem:
    """Operational flight mode definition (Prompt Section 9)."""
    mode_name: str
    mode_code: int
    purpose: str
    propulsion_authority: str
    control_surface_authority: str
    required_sensors: List[str]
    transition_dependency: str
    failsafe_behavior: str
    configuration_status: FlightControlStatus
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode_name": self.mode_name,
            "mode_code": self.mode_code,
            "purpose": self.purpose,
            "propulsion_authority": self.propulsion_authority,
            "control_surface_authority": self.control_surface_authority,
            "required_sensors": self.required_sensors,
            "transition_dependency": self.transition_dependency,
            "failsafe_behavior": self.failsafe_behavior,
            "configuration_status": self.configuration_status.value,
            "notes": self.notes,
        }


@dataclass
class MissionStateMappingItem:
    """Mapping of Phase 1 mission states to ArduPilot modes (Prompt Section 10)."""
    phase1_state: str
    configured_flight_mode: str
    active_propulsion: List[str]
    active_surfaces: List[str]
    sensor_dependencies: List[str]
    transition_condition: str
    exit_condition: str
    abort_condition: str
    failsafe_action: str
    verification_status: FlightControlStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase1_state": self.phase1_state,
            "configured_flight_mode": self.configured_flight_mode,
            "active_propulsion": self.active_propulsion,
            "active_surfaces": self.active_surfaces,
            "sensor_dependencies": self.sensor_dependencies,
            "transition_condition": self.transition_condition,
            "exit_condition": self.exit_condition,
            "abort_condition": self.abort_condition,
            "failsafe_action": self.failsafe_action,
            "verification_status": self.verification_status.value,
        }


@dataclass
class FailsafeScenarioItem:
    """Detailed failsafe scenario specification (Prompt Section 17)."""
    scenario_id: str
    failure_name: str
    detection_mechanism: str
    configured_response: FailsafeResponseAction
    required_sensors: List[str]
    fallback_mode: str
    verification_method: str
    controllability_status: FlightControlStatus
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "failure_name": self.failure_name,
            "detection_mechanism": self.detection_mechanism,
            "configured_response": self.configured_response.value,
            "required_sensors": self.required_sensors,
            "fallback_mode": self.fallback_mode,
            "verification_method": self.verification_method,
            "controllability_status": self.controllability_status.value,
            "notes": self.notes,
        }


@dataclass
class GroundTestChecklistItem:
    """Pre-flight ground bench test task (Prompt Section 25)."""
    test_id: str
    test_name: str
    subsystem: str
    procedure: str
    expected_result: str
    prerequisite: str
    execution_status: GroundTestExecutionStatus = GroundTestExecutionStatus.NOT_EXECUTED
    notes: str = "Physical execution required prior to flight clearance"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "subsystem": self.subsystem,
            "procedure": self.procedure,
            "expected_result": self.expected_result,
            "prerequisite": self.prerequisite,
            "execution_status": self.execution_status.value,
            "notes": self.notes,
        }


@dataclass
class HardwareReconciliationItem:
    """Authoritative BOM vs integration evidence consistency audit (Prompt Section 3)."""
    component_role: str
    phase8_bom_selection: str
    phase8_bom_id: str
    phase8_unit_mass_kg: float
    phase8_protocol: str
    phase9_integration_reference: str
    phase9_report_bom_id: str
    discrepancy_type: str  # NAMING_MISMATCH, PROTOCOL_MISMATCH, ACTUAL_HARDWARE_CONFLICT
    impact_analysis: str
    reconciliation_verdict: FlightControlStatus
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_role": self.component_role,
            "phase8_bom_selection": self.phase8_bom_selection,
            "phase8_bom_id": self.phase8_bom_id,
            "phase8_unit_mass_kg": self.phase8_unit_mass_kg,
            "phase8_protocol": self.phase8_protocol,
            "phase9_integration_reference": self.phase9_integration_reference,
            "phase9_report_bom_id": self.phase9_report_bom_id,
            "discrepancy_type": self.discrepancy_type,
            "impact_analysis": self.impact_analysis,
            "reconciliation_verdict": self.reconciliation_verdict.value,
            "recommendation": self.recommendation,
        }


@dataclass
class PreflightCheckResult:
    """Evaluation result for an individual preflight arming rule (Prompt Section 16 & 21)."""
    rule_id: str
    rule_name: str
    checked_aspect: str
    rule_status: FlightControlStatus
    evidence_or_reason: str
    critical_for_arming: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "checked_aspect": self.checked_aspect,
            "rule_status": self.rule_status.value,
            "evidence_or_reason": self.evidence_or_reason,
            "critical_for_arming": self.critical_for_arming,
        }


@dataclass
class FlightControlVerificationResult:
    """Consolidated verification and compatibility report."""
    output_mapping_passed: bool
    sensor_mapping_passed: bool
    servo_mapping_passed: bool
    parameter_provenance_passed: bool
    transition_configuration_passed: bool
    failsafe_matrix_passed: bool
    battery_configuration_passed: bool
    hardware_reconciliation_passed: bool
    preflight_checks_passed: bool
    total_parameters_count: int
    unresolved_items_count: int
    deferred_items_count: int
    ground_tests_count: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_mapping_passed": self.output_mapping_passed,
            "sensor_mapping_passed": self.sensor_mapping_passed,
            "servo_mapping_passed": self.servo_mapping_passed,
            "parameter_provenance_passed": self.parameter_provenance_passed,
            "transition_configuration_passed": self.transition_configuration_passed,
            "failsafe_matrix_passed": self.failsafe_matrix_passed,
            "battery_configuration_passed": self.battery_configuration_passed,
            "hardware_reconciliation_passed": self.hardware_reconciliation_passed,
            "preflight_checks_passed": self.preflight_checks_passed,
            "total_parameters_count": self.total_parameters_count,
            "unresolved_items_count": self.unresolved_items_count,
            "deferred_items_count": self.deferred_items_count,
            "ground_tests_count": self.ground_tests_count,
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class FlightControlConfigurationResult:
    """Master Phase 10 execution result object."""
    aircraft_name: str
    flight_controller: str
    autopilot: str
    final_verdict: FinalVerdictStatus
    ground_test_readiness: GroundTestReadiness
    parameters: List[ArduPilotParameter]
    motor_outputs: List[MotorOutputAssignment]
    servo_outputs: List[ServoOutputAssignment]
    vtail_mixer: VTailMixerConfiguration
    sensors: List[SensorConfigurationItem]
    flight_modes: List[FlightModeItem]
    mission_states: List[MissionStateMappingItem]
    failsafes: List[FailsafeScenarioItem]
    ground_test_checklist: List[GroundTestChecklistItem]
    hardware_reconciliation: List[HardwareReconciliationItem]
    preflight_checks: List[PreflightCheckResult]
    verification: FlightControlVerificationResult
    deferred_items: List[str] = field(default_factory=list)
    unresolved_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aircraft_name": self.aircraft_name,
            "flight_controller": self.flight_controller,
            "autopilot": self.autopilot,
            "final_verdict": self.final_verdict.value,
            "ground_test_readiness": self.ground_test_readiness.value,
            "parameters_count": len(self.parameters),
            "parameters": [p.to_dict() for p in self.parameters],
            "motor_outputs": [m.to_dict() for m in self.motor_outputs],
            "servo_outputs": [s.to_dict() for s in self.servo_outputs],
            "vtail_mixer": self.vtail_mixer.to_dict(),
            "sensors": [sn.to_dict() for sn in self.sensors],
            "flight_modes": [fm.to_dict() for fm in self.flight_modes],
            "mission_states": [ms.to_dict() for ms in self.mission_states],
            "failsafes": [fs.to_dict() for fs in self.failsafes],
            "ground_test_checklist": [gt.to_dict() for gt in self.ground_test_checklist],
            "hardware_reconciliation": [hr.to_dict() for hr in self.hardware_reconciliation],
            "preflight_checks": [pc.to_dict() for pc in self.preflight_checks],
            "verification": self.verification.to_dict(),
            "deferred_items": self.deferred_items,
            "unresolved_items": self.unresolved_items,
        }
