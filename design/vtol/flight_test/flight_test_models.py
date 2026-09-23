"""
VTOL Phase 12 Domain Models: Controlled Flight Testing & Flight-Envelope Expansion.

Defines typed dataclasses, domain enums, and recursive serialization for
flight configuration, weather conditions, site operating limits, telemetry streams,
flight metrics (hover, transition, cruise, landing), flight envelope management,
flight incident tracking, and multi-phase engineering reconciliations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FlightReadinessStatus(str, Enum):
    """Evaluation status for flight readiness gates."""
    FLIGHT_READY = "FLIGHT_READY"
    FLIGHT_READY_WITH_WARNINGS = "FLIGHT_READY_WITH_WARNINGS"
    FLIGHT_BLOCKED = "FLIGHT_BLOCKED"


class EvidenceStatus(str, Enum):
    """Required evidence classification per Audit Section 3 and Phase 12A Section 23."""
    PHYSICALLY_EXECUTED_AND_LOGGED = "PHYSICALLY_EXECUTED_AND_LOGGED"
    PHYSICALLY_EXECUTED_BUT_DATA_INCOMPLETE = "PHYSICALLY_EXECUTED_BUT_DATA_INCOMPLETE"
    PHYSICAL_GROUND_MEASUREMENT = "PHYSICAL_GROUND_MEASUREMENT"
    PHYSICAL_BENCH_MEASUREMENT = "PHYSICAL_BENCH_MEASUREMENT"
    SYNTHETIC_TEST_DATA = "SYNTHETIC_TEST_DATA"
    PLANNED_NOT_EXECUTED = "PLANNED_NOT_EXECUTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_MEASURED = "NOT_MEASURED"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    UNVERIFIED = "UNVERIFIED"


class DataOrigin(str, Enum):
    """Data provenance origin taxonomy per Audit Section 12."""
    DESIGNED = "DESIGNED"
    DERIVED = "DERIVED"
    SIMULATED = "SIMULATED"
    SYNTHETIC_TEST_DATA = "SYNTHETIC_TEST_DATA"
    PHYSICAL_BENCH_MEASUREMENT = "PHYSICAL_BENCH_MEASUREMENT"
    PHYSICAL_GROUND_MEASUREMENT = "PHYSICAL_GROUND_MEASUREMENT"
    PHYSICALLY_FLIGHT_VALIDATED = "PHYSICALLY_FLIGHT_VALIDATED"


class FlightGateStatus(str, Enum):
    """Evidence-based flight gate lifecycle state per Audit Section 9."""
    NOT_EXECUTED = "NOT_EXECUTED"
    READY = "READY"
    EXECUTED = "EXECUTED"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class FlightGate(str, Enum):
    """Progressive sequential flight testing gates (Prompt Section 39)."""
    GATE_0_GROUND_VERIFIED = "GATE-0: Ground Verification Complete"
    GATE_1_INITIAL_VTOL = "GATE-1: Initial Low-Risk VTOL Lift"
    GATE_2_STABLE_HOVER = "GATE-2: Stable Hover"
    GATE_3_VERTICAL_MANEUVERING = "GATE-3: Vertical Maneuvering"
    GATE_4_FORWARD_FLIGHT = "GATE-4: Low-Speed Forward Flight"
    GATE_5_FIRST_TRANSITION = "GATE-5: First Controlled Transition"
    GATE_6_STABLE_CRUISE = "GATE-6: Fixed-Wing Cruise"
    GATE_7_RETURN_TRANSITION = "GATE-7: Return Transition"
    GATE_8_VTOL_RECOVERY = "GATE-8: VTOL Recovery"
    GATE_9_LANDING = "GATE-9: Controlled VTOL Landing"
    GATE_10_EXPANDED_ENVELOPE = "GATE-10: Expanded Envelope & Repeatability"


class FlightTestStatus(str, Enum):
    """Lifecycle and execution status of individual flight tests."""
    PLANNED = "PLANNED"
    READY = "READY"
    BLOCKED = "BLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    ABORTED = "ABORTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    REQUIRES_RETEST = "REQUIRES_RETEST"


class FlightCampaignVerdict(str, Enum):
    """Master flight test campaign verdict per Audit Section 13."""
    FLIGHT_ENVELOPE_DEMONSTRATED = "FLIGHT_ENVELOPE_DEMONSTRATED"
    FLIGHT_ENVELOPE_PARTIALLY_DEMONSTRATED = "FLIGHT_ENVELOPE_PARTIALLY_DEMONSTRATED"
    FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED = "FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED"
    FLIGHT_TEST_EVIDENCE_INCOMPLETE = "FLIGHT_TEST_EVIDENCE_INCOMPLETE"
    FLIGHT_TEST_CAMPAIGN_IN_PROGRESS = "FLIGHT_TEST_CAMPAIGN_IN_PROGRESS"
    FLIGHT_TEST_COMPLETE_WITH_WARNINGS = "FLIGHT_TEST_COMPLETE_WITH_WARNINGS"
    FLIGHT_TEST_BLOCKED = "FLIGHT_TEST_BLOCKED"
    FLIGHT_TEST_FAILED = "FLIGHT_TEST_FAILED"


class IncidentSeverity(str, Enum):
    """Severity classification for flight anomalies and incidents."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class IncidentStatus(str, Enum):
    """Resolution status of flight incidents."""
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    CLOSED = "CLOSED"
    ACCEPTED_LIMITATION = "ACCEPTED_LIMITATION"


class StructuralInspectionStatus(str, Enum):
    """Post-flight airframe and linkage physical inspection status."""
    NO_DAMAGE = "NO_DAMAGE"
    DAMAGE_DETECTED = "DAMAGE_DETECTED"
    INSPECTION_REQUIRED = "INSPECTION_REQUIRED"


class ControlAssessment(str, Enum):
    """Quantitative stability and control assessment classification."""
    CONTROLLED = "CONTROLLED"
    MARGINAL = "MARGINAL"
    UNSTABLE = "UNSTABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ModelReconciliationAction(str, Enum):
    """Recommended actions when flight measurements diverge from engineering models."""
    NO_CHANGE = "NO_CHANGE"
    MONITOR = "MONITOR"
    MODEL_REVIEW_REQUIRED = "MODEL_REVIEW_REQUIRED"
    UPSTREAM_CHANGE_REQUIRED = "UPSTREAM_CHANGE_REQUIRED"


class TransitionEvaluation(str, Enum):
    """Correlation status of measured flight transition vs Phase 3 model."""
    MODEL_MATCH = "MODEL_MATCH"
    MODEL_DEVIATION = "MODEL_DEVIATION"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(slots=True)
class OperatingLimits:
    """Pre-established physical and environmental site operating boundaries."""
    max_permitted_wind_mps: float = 7.0
    max_permitted_gust_mps: float = 9.0
    min_visibility_km: float = 5.0
    min_field_area_m2: float = 2500.0
    max_test_altitude_m_agl: float = 50.0
    max_horizontal_distance_m: float = 300.0
    min_battery_reserve_pct: float = 25.0
    max_ambient_temp_c: float = 38.0
    min_ambient_temp_c: float = 5.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_permitted_wind_mps": self.max_permitted_wind_mps,
            "max_permitted_gust_mps": self.max_permitted_gust_mps,
            "min_visibility_km": self.min_visibility_km,
            "min_field_area_m2": self.min_field_area_m2,
            "max_test_altitude_m_agl": self.max_test_altitude_m_agl,
            "max_horizontal_distance_m": self.max_horizontal_distance_m,
            "min_battery_reserve_pct": self.min_battery_reserve_pct,
            "max_ambient_temp_c": self.max_ambient_temp_c,
            "min_ambient_temp_c": self.min_ambient_temp_c,
        }


@dataclass(slots=True)
class WeatherConditions:
    """Observed environmental and atmospheric conditions during flight testing."""
    temperature_c: float
    wind_speed_mps: float
    wind_direction_deg: float
    wind_gust_mps: float
    humidity_pct: float
    visibility_km: float
    field_condition: str = "Dry short-grass runway with unobstructed obstacle clearance"
    within_limits: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature_c": self.temperature_c,
            "wind_speed_mps": self.wind_speed_mps,
            "wind_direction_deg": self.wind_direction_deg,
            "wind_gust_mps": self.wind_gust_mps,
            "humidity_pct": self.humidity_pct,
            "visibility_km": self.visibility_km,
            "field_condition": self.field_condition,
            "within_limits": self.within_limits,
        }


@dataclass(slots=True)
class FlightConfiguration:
    """Traceable configuration version for individual flight sorties (Prompt Section 6)."""
    aircraft_id: str
    flight_id: str
    ardupilot_firmware: str
    parameter_file_hash: str
    phase10_config_rev: str
    phase11_hardware_rev: str
    battery_id: str
    battery_initial_voltage_v: float
    battery_initial_soc_pct: float
    payload_weight_kg: float
    aircraft_mass_kg: float
    cg_x_m: float
    pilot_in_command: str
    test_observer: str
    test_engineer: str
    date_time_iso: str
    location_name: str
    weather_summary: str
    test_objective: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aircraft_id": self.aircraft_id,
            "flight_id": self.flight_id,
            "ardupilot_firmware": self.ardupilot_firmware,
            "parameter_file_hash": self.parameter_file_hash,
            "phase10_config_rev": self.phase10_config_rev,
            "phase11_hardware_rev": self.phase11_hardware_rev,
            "battery_id": self.battery_id,
            "battery_initial_voltage_v": self.battery_initial_voltage_v,
            "battery_initial_soc_pct": self.battery_initial_soc_pct,
            "payload_weight_kg": self.payload_weight_kg,
            "aircraft_mass_kg": self.aircraft_mass_kg,
            "cg_x_m": self.cg_x_m,
            "pilot_in_command": self.pilot_in_command,
            "test_observer": self.test_observer,
            "test_engineer": self.test_engineer,
            "date_time_iso": self.date_time_iso,
            "location_name": self.location_name,
            "weather_summary": self.weather_summary,
            "test_objective": self.test_objective,
        }


@dataclass(slots=True)
class ReadinessSubsystemCheck:
    """Individual gate check item evaluated before flight authorization."""
    subsystem: str
    category: str  # "Aircraft", "Avionics", "Software", "Environment", "Operational"
    status: FlightReadinessStatus
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subsystem": self.subsystem,
            "category": self.category,
            "status": self.status.value,
            "details": self.details,
        }


@dataclass(slots=True)
class FlightReadinessReport:
    """Comprehensive readiness gate report evaluated prior to any takeoff."""
    overall_status: FlightReadinessStatus
    checks: List[ReadinessSubsystemCheck]
    blockers: List[str]
    warnings: List[str]
    gate_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "checks": [c.to_dict() for c in self.checks],
            "blockers": self.blockers,
            "warnings": self.warnings,
            "gate_name": self.gate_name,
        }


@dataclass(slots=True)
class FlightTelemetryPoint:
    """Synchronized flight-data telemetry sample point."""
    timestamp_s: float
    altitude_agl_m: float
    climb_rate_mps: float
    pitch_deg: float
    roll_deg: float
    yaw_deg: float
    pitch_rate_dps: float
    roll_rate_dps: float
    yaw_rate_dps: float
    throttle_pct: float
    m1_lift_output: float
    m2_lift_output: float
    m3_lift_output: float
    m4_lift_output: float
    m5_cruise_output: float
    left_aileron_deg: float
    right_aileron_deg: float
    left_ruddervator_deg: float
    right_ruddervator_deg: float
    battery_voltage_v: float
    battery_current_a: float
    calibrated_airspeed_mps: float
    groundspeed_mps: float
    vibration_x: float
    vibration_y: float
    vibration_z: float
    ekf_status: str = "EKF3_NOMINAL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp_s": self.timestamp_s,
            "altitude_agl_m": self.altitude_agl_m,
            "climb_rate_mps": self.climb_rate_mps,
            "pitch_deg": self.pitch_deg,
            "roll_deg": self.roll_deg,
            "yaw_deg": self.yaw_deg,
            "pitch_rate_dps": self.pitch_rate_dps,
            "roll_rate_dps": self.roll_rate_dps,
            "yaw_rate_dps": self.yaw_rate_dps,
            "throttle_pct": self.throttle_pct,
            "m1_lift_output": self.m1_lift_output,
            "m2_lift_output": self.m2_lift_output,
            "m3_lift_output": self.m3_lift_output,
            "m4_lift_output": self.m4_lift_output,
            "m5_cruise_output": self.m5_cruise_output,
            "left_aileron_deg": self.left_aileron_deg,
            "right_aileron_deg": self.right_aileron_deg,
            "left_ruddervator_deg": self.left_ruddervator_deg,
            "right_ruddervator_deg": self.right_ruddervator_deg,
            "battery_voltage_v": self.battery_voltage_v,
            "battery_current_a": self.battery_current_a,
            "calibrated_airspeed_mps": self.calibrated_airspeed_mps,
            "groundspeed_mps": self.groundspeed_mps,
            "vibration_x": self.vibration_x,
            "vibration_y": self.vibration_y,
            "vibration_z": self.vibration_z,
            "ekf_status": self.ekf_status,
        }


@dataclass(slots=True)
class HoverMetrics:
    """Quantitative hover flight metrics (Prompt Section 11 & 24)."""
    flight_id: str
    duration_s: float
    mean_pitch_deg: float
    mean_roll_deg: float
    mean_yaw_deg: float
    rms_attitude_error_deg: float
    max_attitude_excursion_deg: float
    mean_throttle_pct: float
    mean_current_a: float
    mean_voltage_v: float
    mean_electrical_power_w: float
    hover_efficiency_g_per_w: float
    control_assessment: ControlAssessment = ControlAssessment.CONTROLLED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flight_id": self.flight_id,
            "duration_s": self.duration_s,
            "mean_pitch_deg": self.mean_pitch_deg,
            "mean_roll_deg": self.mean_roll_deg,
            "mean_yaw_deg": self.mean_yaw_deg,
            "rms_attitude_error_deg": self.rms_attitude_error_deg,
            "max_attitude_excursion_deg": self.max_attitude_excursion_deg,
            "mean_throttle_pct": self.mean_throttle_pct,
            "mean_current_a": self.mean_current_a,
            "mean_voltage_v": self.mean_voltage_v,
            "mean_electrical_power_w": self.mean_electrical_power_w,
            "hover_efficiency_g_per_w": self.hover_efficiency_g_per_w,
            "control_assessment": self.control_assessment.value,
        }


@dataclass(slots=True)
class TransitionMetrics:
    """Quantitative transition flight metrics (Prompt Section 17, 18, 20 & 24)."""
    flight_id: str
    transition_type: str  # "FORWARD_ACCEL", "INBOUND_BACK_TRANSITION"
    transition_duration_s: float
    start_airspeed_mps: float
    handover_airspeed_mps: float
    min_altitude_m_agl: float
    altitude_loss_m: float
    max_attitude_excursion_deg: float
    peak_current_a: float
    peak_electrical_power_w: float
    mean_electrical_power_w: float
    abort_mechanism_tested: bool
    abort_response_time_s: Optional[float]
    correlation_evaluation: TransitionEvaluation = TransitionEvaluation.MODEL_MATCH

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flight_id": self.flight_id,
            "transition_type": self.transition_type,
            "transition_duration_s": self.transition_duration_s,
            "start_airspeed_mps": self.start_airspeed_mps,
            "handover_airspeed_mps": self.handover_airspeed_mps,
            "min_altitude_m_agl": self.min_altitude_m_agl,
            "altitude_loss_m": self.altitude_loss_m,
            "max_attitude_excursion_deg": self.max_attitude_excursion_deg,
            "peak_current_a": self.peak_current_a,
            "peak_electrical_power_w": self.peak_electrical_power_w,
            "mean_electrical_power_w": self.mean_electrical_power_w,
            "abort_mechanism_tested": self.abort_mechanism_tested,
            "abort_response_time_s": self.abort_response_time_s,
            "correlation_evaluation": self.correlation_evaluation.value,
        }


@dataclass(slots=True)
class CruiseMetrics:
    """Quantitative fixed-wing cruise flight metrics (Prompt Section 19 & 24)."""
    flight_id: str
    duration_s: float
    mean_calibrated_airspeed_mps: float
    mean_groundspeed_mps: float
    mean_cruise_power_w: float
    mean_current_a: float
    energy_consumed_wh: float
    specific_energy_wh_per_km: float
    projected_endurance_min: float
    control_assessment: ControlAssessment = ControlAssessment.CONTROLLED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flight_id": self.flight_id,
            "duration_s": self.duration_s,
            "mean_calibrated_airspeed_mps": self.mean_calibrated_airspeed_mps,
            "mean_groundspeed_mps": self.mean_groundspeed_mps,
            "mean_cruise_power_w": self.mean_cruise_power_w,
            "mean_current_a": self.mean_current_a,
            "energy_consumed_wh": self.energy_consumed_wh,
            "specific_energy_wh_per_km": self.specific_energy_wh_per_km,
            "projected_endurance_min": self.projected_endurance_min,
            "control_assessment": self.control_assessment.value,
        }


@dataclass(slots=True)
class LandingMetrics:
    """Quantitative vertical landing metrics (Prompt Section 22 & 24)."""
    flight_id: str
    touchdown_descent_rate_mps: float
    attitude_at_touchdown_deg: float
    final_battery_voltage_v: float
    final_battery_reserve_pct: float
    structural_status: StructuralInspectionStatus = StructuralInspectionStatus.NO_DAMAGE
    thermal_inspection_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flight_id": self.flight_id,
            "touchdown_descent_rate_mps": self.touchdown_descent_rate_mps,
            "attitude_at_touchdown_deg": self.attitude_at_touchdown_deg,
            "final_battery_voltage_v": self.final_battery_voltage_v,
            "final_battery_reserve_pct": self.final_battery_reserve_pct,
            "structural_status": self.structural_status.value,
            "thermal_inspection_notes": self.thermal_inspection_notes,
        }


@dataclass(slots=True)
class FlightEnvelope:
    """Demonstrated empirical flight-envelope boundaries (Prompt Section 30)."""
    is_established: bool = False
    status: str = "NOT_ESTABLISHED"
    min_demonstrated_airspeed_mps: float = 0.0
    max_demonstrated_airspeed_mps: float = 0.0
    max_demonstrated_altitude_m_agl: float = 0.0
    max_demonstrated_climb_rate_mps: float = 0.0
    max_demonstrated_descent_rate_mps: float = 0.0
    max_demonstrated_bank_angle_deg: float = 0.0
    max_demonstrated_pitch_angle_deg: float = 0.0
    max_demonstrated_current_a: float = 0.0
    max_demonstrated_power_w: float = 0.0
    min_demonstrated_battery_reserve_pct: float = 100.0
    demonstrated_transition_entry_speed_mps: float = 0.0
    demonstrated_transition_exit_speed_mps: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_established": self.is_established,
            "status": self.status,
            "min_demonstrated_airspeed_mps": self.min_demonstrated_airspeed_mps,
            "max_demonstrated_airspeed_mps": self.max_demonstrated_airspeed_mps,
            "max_demonstrated_altitude_m_agl": self.max_demonstrated_altitude_m_agl,
            "max_demonstrated_climb_rate_mps": self.max_demonstrated_climb_rate_mps,
            "max_demonstrated_descent_rate_mps": self.max_demonstrated_descent_rate_mps,
            "max_demonstrated_bank_angle_deg": self.max_demonstrated_bank_angle_deg,
            "max_demonstrated_pitch_angle_deg": self.max_demonstrated_pitch_angle_deg,
            "max_demonstrated_current_a": self.max_demonstrated_current_a,
            "max_demonstrated_power_w": self.max_demonstrated_power_w,
            "min_demonstrated_battery_reserve_pct": self.min_demonstrated_battery_reserve_pct,
            "demonstrated_transition_entry_speed_mps": self.demonstrated_transition_entry_speed_mps,
            "demonstrated_transition_exit_speed_mps": self.demonstrated_transition_exit_speed_mps,
        }


@dataclass(slots=True)
class FlightIncident:
    """Structured incident record for anomalies and safety events (Prompt Section 35)."""
    incident_id: str
    flight_id: str
    timestamp_iso: str
    flight_phase: str
    severity: IncidentSeverity
    condition: str
    observed_behavior: str
    telemetry_evidence: str
    possible_cause: str
    aircraft_state: str
    action_taken: str
    damage: str
    follow_up: str
    status: IncidentStatus = IncidentStatus.OPEN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "flight_id": self.flight_id,
            "timestamp_iso": self.timestamp_iso,
            "flight_phase": self.flight_phase,
            "severity": self.severity.value,
            "condition": self.condition,
            "observed_behavior": self.observed_behavior,
            "telemetry_evidence": self.telemetry_evidence,
            "possible_cause": self.possible_cause,
            "aircraft_state": self.aircraft_state,
            "action_taken": self.action_taken,
            "damage": self.damage,
            "follow_up": self.follow_up,
            "status": self.status.value,
        }


@dataclass(slots=True)
class EngineeringReconciliation:
    """Traceable reconciliation between measured flight data and upstream engineering models (Prompt Section 36)."""
    parameter_name: str
    upstream_phase: str
    predicted_value: str
    measured_value: str
    delta: str
    significance: str
    confidence: str
    action: ModelReconciliationAction
    evidence_origin: DataOrigin = DataOrigin.DESIGNED
    evidence_status: EvidenceStatus = EvidenceStatus.UNVERIFIED
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "upstream_phase": self.upstream_phase,
            "predicted_value": self.predicted_value,
            "measured_value": self.measured_value,
            "delta": self.delta,
            "significance": self.significance,
            "confidence": self.confidence,
            "action": self.action.value,
            "evidence_origin": self.evidence_origin.value,
            "evidence_status": self.evidence_status.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class FlightSortieRecord:
    """Master record for a single flight test sortie."""
    flight_id: str
    flight_number: int
    gate_associated: FlightGate
    status: FlightTestStatus
    configuration: FlightConfiguration
    weather: WeatherConditions
    start_time_iso: str
    end_time_iso: str
    duration_s: float
    max_altitude_m_agl: float
    max_groundspeed_mps: float
    max_airspeed_mps: float
    dataflash_log_filename: str
    evidence_status: EvidenceStatus = EvidenceStatus.PLANNED_NOT_EXECUTED
    data_origin: DataOrigin = DataOrigin.DESIGNED
    log_source_verified: bool = False
    hover_metrics: Optional[HoverMetrics] = None
    transition_metrics: Optional[TransitionMetrics] = None
    cruise_metrics: Optional[CruiseMetrics] = None
    landing_metrics: Optional[LandingMetrics] = None
    structural_inspection: StructuralInspectionStatus = StructuralInspectionStatus.NO_DAMAGE
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flight_id": self.flight_id,
            "flight_number": self.flight_number,
            "gate_associated": self.gate_associated.value,
            "status": self.status.value,
            "configuration": self.configuration.to_dict(),
            "weather": self.weather.to_dict(),
            "start_time_iso": self.start_time_iso,
            "end_time_iso": self.end_time_iso,
            "duration_s": self.duration_s,
            "max_altitude_m_agl": self.max_altitude_m_agl,
            "max_groundspeed_mps": self.max_groundspeed_mps,
            "max_airspeed_mps": self.max_airspeed_mps,
            "dataflash_log_filename": self.dataflash_log_filename,
            "evidence_status": self.evidence_status.value,
            "data_origin": self.data_origin.value,
            "log_source_verified": self.log_source_verified,
            "hover_metrics": self.hover_metrics.to_dict() if self.hover_metrics else None,
            "transition_metrics": self.transition_metrics.to_dict() if self.transition_metrics else None,
            "cruise_metrics": self.cruise_metrics.to_dict() if self.cruise_metrics else None,
            "landing_metrics": self.landing_metrics.to_dict() if self.landing_metrics else None,
            "structural_inspection": self.structural_inspection.value,
            "notes": self.notes,
        }


@dataclass(slots=True)
class FlightCampaignState:
    """Master state representing the complete Phase 12 controlled flight test campaign."""
    aircraft_name: str
    campaign_name: str
    active_gate: FlightGate
    completed_gates: List[FlightGate]
    sorties: List[FlightSortieRecord]
    demonstrated_envelope: FlightEnvelope
    incidents: List[FlightIncident]
    reconciliations: List[EngineeringReconciliation]
    current_readiness: FlightReadinessReport
    site_limits: OperatingLimits
    campaign_verdict: FlightCampaignVerdict
    verdict_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aircraft_name": self.aircraft_name,
            "campaign_name": self.campaign_name,
            "active_gate": self.active_gate.value,
            "completed_gates": [g.value for g in self.completed_gates],
            "sorties": [s.to_dict() for s in self.sorties],
            "demonstrated_envelope": self.demonstrated_envelope.to_dict(),
            "incidents": [i.to_dict() for i in self.incidents],
            "reconciliations": [r.to_dict() for r in self.reconciliations],
            "current_readiness": self.current_readiness.to_dict(),
            "site_limits": self.site_limits.to_dict(),
            "campaign_verdict": self.campaign_verdict.value,
            "verdict_explanation": self.verdict_explanation,
        }


@dataclass(slots=True)
class DataFlashLogMetadata:
    """Provenance and cryptographic integrity metadata for ingested DataFlash log files."""
    filename: str
    filepath: str
    file_size_bytes: int
    sha256_hash: str
    ingestion_timestamp_iso: str
    flight_id: str
    log_format: str  # "DATAFLASH_BIN", "DATAFLASH_CSV", "TELEMETRY_LOG"
    firmware_version: Optional[str] = None
    vehicle_id: Optional[str] = None
    start_time_iso: Optional[str] = None
    end_time_iso: Optional[str] = None
    duration_s: float = 0.0
    airborne_duration_s: float = 0.0
    parser_version: str = "TorqWings-DF-1.0"
    extraction_status: str = "NOT_EXTRACTED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "filepath": self.filepath,
            "file_size_bytes": self.file_size_bytes,
            "sha256_hash": self.sha256_hash,
            "ingestion_timestamp_iso": self.ingestion_timestamp_iso,
            "flight_id": self.flight_id,
            "log_format": self.log_format,
            "firmware_version": self.firmware_version,
            "vehicle_id": self.vehicle_id,
            "start_time_iso": self.start_time_iso,
            "end_time_iso": self.end_time_iso,
            "duration_s": self.duration_s,
            "airborne_duration_s": self.airborne_duration_s,
            "parser_version": self.parser_version,
            "extraction_status": self.extraction_status,
        }


@dataclass(slots=True)
class MetricProvenance:
    """Rigorous source provenance tracking for every measured flight metric (Prompt Section 4)."""
    metric_name: str
    value: Any
    unit: str
    source_log: str
    source_message_type: str
    source_field: str
    sample_range_or_time: str
    calculation_method: str
    evidence_status: EvidenceStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "source_log": self.source_log,
            "source_message_type": self.source_message_type,
            "source_field": self.source_field,
            "sample_range_or_time": self.sample_range_or_time,
            "calculation_method": self.calculation_method,
            "evidence_status": self.evidence_status.value,
        }

