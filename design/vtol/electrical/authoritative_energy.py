"""
VTOL Authoritative Mission Energy, Battery Sizing & Electrical Integration Subsystem.

Purpose:
    Provides the single authoritative, configuration-driven, manufacturer-independent
    engineering model for VTOL mission energy accounting, battery sizing, electrical
    buses, and current/power envelopes (Lift + Cruise / QuadPlane architecture).

Authoritative Upstream Sources Consumed:
    1. Phase 2 Authoritative Hover Model: Hover electrical power (P_hover_elec), hover current,
       lift motor count (N), per-motor thrust.
    2. Phase 3 Authoritative Transition Model: Trapezoidal integrated corridor energy (E_trans),
       peak electrical power, forward and vertical power profiles for both directions
       (TRANSITION_TO_CRUISE and TRANSITION_TO_VTOL).
    3. Fixed-Wing Engineering Adapter / Cruise Propulsion: Authoritative cruise propulsion power
       (P_cruise_elec) and operating voltage/current.

Key Design Invariants:
    - Exactly one authoritative owner per mission segment (Zero double counting).
    - No phantom physics: parameters not yet defined are reported as UNRESOLVED or explicit assumptions.
    - Manufacturer-independent sizing: sizes required energy (Wh), usable energy, nominal energy,
      capacity (Ah), continuous/peak current (A), and C-rate. Commercial battery selection is deferred.
    - Pre-convergence MTOW boundary preserved: uses sizing_mass_kg with is_converged_mtow = False.
    - Full recursive serialization for all ledger entries, envelopes, and sizing metrics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import math

from backend.design.vtol.mission.mission_state import VTOLMissionPhase, VTOLMissionProfileSequence

GRAVITATIONAL_ACCELERATION_M_S2: float = 9.80665
DEFAULT_RESERVE_FRACTION: float = 0.20        # Standard 20% mission reserve energy
DEFAULT_USABLE_DOD_FRACTION: float = 0.85     # Max 85% allowable depth of discharge (DoD)
DEFAULT_AVIONICS_POWER_W: float = 40.0        # Autopilot, sensors, BEC losses, telemetry
DEFAULT_PAYLOAD_POWER_W: float = 0.0          # Unpowered standard payload default


class EnergyLedgerValidationError(ValueError):
    """Raised when mission energy or electrical sizing violates engineering invariants."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass(slots=True)
class MissionEnergySegment:
    """
    Authoritative energy and power accounting for an individual mission flight phase.
    """
    phase: VTOLMissionPhase
    duration_s: float
    average_power_w: float
    peak_power_w: float
    energy_wh: float
    propulsion_power_w: float = 0.0
    avionics_power_w: float = 0.0
    payload_power_w: float = 0.0
    power_source: str = "BATTERY"
    calculation_source: str = "UNKNOWN"
    load_type: str = "PROPULSION_AND_AVIONICS"  # OFF, AVIONICS_ONLY, PROPULSION_ONLY, PROPULSION_AND_AVIONICS, DUAL_BUS_BLENDED
    status: str = "IMPLEMENTED"                  # IMPLEMENTED, ESTIMATED, UNSUPPORTED, MISSING_INPUT
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value if isinstance(self.phase, Enum) else str(self.phase),
            "duration_s": round(self.duration_s, 2),
            "average_power_w": round(self.average_power_w, 2),
            "peak_power_w": round(self.peak_power_w, 2),
            "energy_wh": round(self.energy_wh, 3),
            "propulsion_power_w": round(self.propulsion_power_w, 2),
            "avionics_power_w": round(self.avionics_power_w, 2),
            "payload_power_w": round(self.payload_power_w, 2),
            "power_source": self.power_source,
            "calculation_source": self.calculation_source,
            "load_type": self.load_type,
            "status": self.status,
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class MissionEnergyLedger:
    """
    Complete 10-phase authoritative mission energy ledger.
    """
    segments: List[MissionEnergySegment]
    total_mission_duration_s: float
    total_propulsion_energy_wh: float
    total_avionics_energy_wh: float
    total_payload_energy_wh: float
    total_mission_energy_wh: float
    is_complete: bool
    has_double_counting: bool
    status: str = "IMPLEMENTED"
    validation_messages: List[str] = field(default_factory=list)

    def get_segment(self, phase: VTOLMissionPhase) -> Optional[MissionEnergySegment]:
        for s in self.segments:
            if s.phase == phase:
                return s
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segments": [s.to_dict() for s in self.segments],
            "total_mission_duration_s": round(self.total_mission_duration_s, 2),
            "total_propulsion_energy_wh": round(self.total_propulsion_energy_wh, 3),
            "total_avionics_energy_wh": round(self.total_avionics_energy_wh, 3),
            "total_payload_energy_wh": round(self.total_payload_energy_wh, 3),
            "total_mission_energy_wh": round(self.total_mission_energy_wh, 3),
            "is_complete": self.is_complete,
            "has_double_counting": self.has_double_counting,
            "status": self.status,
            "validation_messages": list(self.validation_messages),
        }


@dataclass(slots=True)
class BatterySizingRequirements:
    """
    Manufacturer-independent battery system sizing requirements.
    """
    mission_energy_wh: float
    reserve_fraction: float
    reserve_energy_wh: float
    required_usable_energy_wh: float
    usable_fraction: float
    required_nominal_battery_energy_wh: float
    nominal_voltage_v: Optional[float] = None
    required_usable_capacity_ah: Optional[float] = None
    required_nominal_capacity_ah: Optional[float] = None
    specific_energy_wh_kg: Optional[float] = None
    estimated_battery_mass_kg: Optional[float] = None
    battery_mass_status: str = "UNRESOLVED_DEFERRED_TO_PHASE5"
    status: str = "IMPLEMENTED"
    engineering_assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_energy_wh": round(self.mission_energy_wh, 3),
            "reserve_fraction": round(self.reserve_fraction, 4),
            "reserve_energy_wh": round(self.reserve_energy_wh, 3),
            "required_usable_energy_wh": round(self.required_usable_energy_wh, 3),
            "usable_fraction": round(self.usable_fraction, 4),
            "required_nominal_battery_energy_wh": round(self.required_nominal_battery_energy_wh, 3),
            "nominal_voltage_v": round(self.nominal_voltage_v, 2) if self.nominal_voltage_v is not None else None,
            "required_usable_capacity_ah": round(self.required_usable_capacity_ah, 3) if self.required_usable_capacity_ah is not None else None,
            "required_nominal_capacity_ah": round(self.required_nominal_capacity_ah, 3) if self.required_nominal_capacity_ah is not None else None,
            "specific_energy_wh_kg": round(self.specific_energy_wh_kg, 2) if self.specific_energy_wh_kg is not None else None,
            "estimated_battery_mass_kg": round(self.estimated_battery_mass_kg, 3) if self.estimated_battery_mass_kg is not None else None,
            "battery_mass_status": self.battery_mass_status,
            "status": self.status,
            "engineering_assumptions": list(self.engineering_assumptions),
            "warnings": list(self.warnings),
        }


@dataclass(slots=True)
class ElectricalBusMetrics:
    """
    Operating power, current, and motor load breakdown for a discrete electrical propulsion bus.
    """
    bus_name: str
    continuous_power_w: float
    peak_power_w: float
    continuous_current_a: Optional[float] = None
    peak_current_a: Optional[float] = None
    motor_count: int = 1
    per_motor_current_a: Optional[float] = None
    subsystems_connected: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bus_name": self.bus_name,
            "continuous_power_w": round(self.continuous_power_w, 2),
            "peak_power_w": round(self.peak_power_w, 2),
            "continuous_current_a": round(self.continuous_current_a, 2) if self.continuous_current_a is not None else None,
            "peak_current_a": round(self.peak_current_a, 2) if self.peak_current_a is not None else None,
            "motor_count": self.motor_count,
            "per_motor_current_a": round(self.per_motor_current_a, 2) if self.per_motor_current_a is not None else None,
            "subsystems_connected": list(self.subsystems_connected),
        }


@dataclass(slots=True)
class ElectricalEnvelope:
    """
    Consolidated power, current, C-rate, and bus envelope across the entire VTOL mission.
    """
    mission_average_power_w: float
    maximum_continuous_power_w: float
    maximum_peak_power_w: float
    continuous_current_a: Optional[float] = None
    peak_current_a: Optional[float] = None
    continuous_c_rate: Optional[float] = None
    peak_c_rate: Optional[float] = None
    c_rate_limit: Optional[float] = None
    is_c_rate_compliant: Optional[bool] = None
    lift_bus: Optional[ElectricalBusMetrics] = None
    cruise_bus: Optional[ElectricalBusMetrics] = None
    avionics_bus: Optional[ElectricalBusMetrics] = None
    simultaneous_transition_power_w: float = 0.0
    simultaneous_transition_current_a: Optional[float] = None
    status: str = "IMPLEMENTED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_average_power_w": round(self.mission_average_power_w, 2),
            "maximum_continuous_power_w": round(self.maximum_continuous_power_w, 2),
            "maximum_peak_power_w": round(self.maximum_peak_power_w, 2),
            "continuous_current_a": round(self.continuous_current_a, 2) if self.continuous_current_a is not None else None,
            "peak_current_a": round(self.peak_current_a, 2) if self.peak_current_a is not None else None,
            "continuous_c_rate": round(self.continuous_c_rate, 2) if self.continuous_c_rate is not None else None,
            "peak_c_rate": round(self.peak_c_rate, 2) if self.peak_c_rate is not None else None,
            "c_rate_limit": round(self.c_rate_limit, 2) if self.c_rate_limit is not None else None,
            "is_c_rate_compliant": self.is_c_rate_compliant,
            "lift_bus": self.lift_bus.to_dict() if self.lift_bus else None,
            "cruise_bus": self.cruise_bus.to_dict() if self.cruise_bus else None,
            "avionics_bus": self.avionics_bus.to_dict() if self.avionics_bus else None,
            "simultaneous_transition_power_w": round(self.simultaneous_transition_power_w, 2),
            "simultaneous_transition_current_a": round(self.simultaneous_transition_current_a, 2) if self.simultaneous_transition_current_a is not None else None,
            "status": self.status,
        }


@dataclass(slots=True)
class AuthoritativeEnergyResult:
    """
    Consolidated Phase 4 engineering outputs for energy, battery, and electrical sizing.
    """
    sizing_mass_kg: float
    aircraft_weight_n: float
    lift_motor_count: int
    ledger: MissionEnergyLedger
    battery_sizing: BatterySizingRequirements
    envelope: ElectricalEnvelope
    is_converged_mtow: bool = False
    mtow_status: str = "PRE_CONVERGENCE_SIZING"
    status: str = "IMPLEMENTED"
    engineering_assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    parameter_provenance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sizing_mass_kg": round(self.sizing_mass_kg, 4),
            "aircraft_weight_n": round(self.aircraft_weight_n, 3),
            "lift_motor_count": self.lift_motor_count,
            "ledger": self.ledger.to_dict(),
            "battery_sizing": self.battery_sizing.to_dict(),
            "envelope": self.envelope.to_dict(),
            "is_converged_mtow": self.is_converged_mtow,
            "mtow_status": self.mtow_status,
            "status": self.status,
            "engineering_assumptions": list(self.engineering_assumptions),
            "parameter_provenance": {k: dict(v) for k, v in self.parameter_provenance.items()},
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "metadata": dict(self.metadata),
        }


class AuthoritativeEnergyModel:
    """
    Authoritative engineering calculation engine for VTOL Phase 4 mission energy and battery sizing.
    """

    @classmethod
    def calculate_mission_energy(
        cls,
        sizing_mass_kg: float,
        lift_motor_count: int = 4,
        mission_profile_sequence: Optional[VTOLMissionProfileSequence] = None,
        hover_result: Optional[Any] = None,
        transition_result: Optional[Any] = None,
        reverse_transition_result: Optional[Any] = None,
        cruise_propulsion_power_w: Optional[float] = None,
        loiter_propulsion_power_w: Optional[float] = None,
        system_voltage_v: Optional[float] = None,
        avionics_power_w: Optional[float] = None,
        payload_power_w: Optional[float] = None,
        reserve_fraction: float = DEFAULT_RESERVE_FRACTION,
        usable_fraction: float = DEFAULT_USABLE_DOD_FRACTION,
        specific_energy_wh_kg: Optional[float] = None,
        max_allowable_c_rate: Optional[float] = None,
        custom_segment_durations_s: Optional[Dict[VTOLMissionPhase, float]] = None,
        avionics_power_provenance: Optional[str] = None,
        payload_power_provenance: Optional[str] = None,
        reserve_fraction_provenance: Optional[str] = None,
        usable_fraction_provenance: Optional[str] = None,
    ) -> AuthoritativeEnergyResult:
        """
        Synthesizes the complete 10-phase mission energy ledger, sizes the battery requirements,
        and computes the electrical envelope with explicit parameter provenance tracking.
        """
        errors: List[str] = []
        warnings: List[str] = []
        assumptions: List[str] = []

        # 1. Invariant validations
        if sizing_mass_kg <= 0.0:
            errors.append(f"Invalid sizing mass: {sizing_mass_kg} kg <= 0.0.")
        if lift_motor_count <= 0:
            errors.append(f"Invalid lift motor count: {lift_motor_count} <= 0.")
        if reserve_fraction < 0.0:
            errors.append(f"Invalid reserve fraction: {reserve_fraction}. Must be non-negative (>= 0.0).")
        if usable_fraction <= 0.0 or usable_fraction > 1.0:
            errors.append(f"Invalid usable DoD fraction: {usable_fraction}. Must be in (0.0, 1.0].")
        if system_voltage_v is not None and system_voltage_v <= 0.0:
            errors.append(f"Invalid system voltage: {system_voltage_v} V <= 0.0.")

        if errors:
            raise EnergyLedgerValidationError(errors)

        aircraft_weight_n = sizing_mass_kg * GRAVITATIONAL_ACCELERATION_M_S2

        # 2. Resolve Auxiliary Loads (Avionics & Payload) and Track Provenance
        if avionics_power_w is not None:
            actual_avionics_w = float(avionics_power_w)
            actual_avionics_provenance = avionics_power_provenance or "CONFIGURABLE_ASSUMPTION"
            actual_avionics_source = (
                "AVIONICS_SUBSYSTEM_ANALYSIS"
                if actual_avionics_provenance == "DERIVED"
                else "USER_CONFIGURED_INPUT"
            )
            assumptions.append(
                f"Avionics electrical load set to {actual_avionics_w:.1f} W "
                f"(Provenance: {actual_avionics_provenance}, source: {actual_avionics_source})."
            )
        else:
            actual_avionics_w = DEFAULT_AVIONICS_POWER_W
            actual_avionics_provenance = "UNRESOLVED_INPUT"
            actual_avionics_source = f"DEFAULT_CONFIGURABLE_FALLBACK ({DEFAULT_AVIONICS_POWER_W:.1f}W)"
            assumptions.append(
                f"Avionics electrical load is an UNRESOLVED_INPUT (no upstream avionics synthesis output provided); "
                f"using configurable baseline assumption of {DEFAULT_AVIONICS_POWER_W:.1f} W."
            )

        if payload_power_w is not None:
            actual_payload_w = float(payload_power_w)
            actual_payload_provenance = payload_power_provenance or "CONFIGURABLE_ASSUMPTION"
            actual_payload_source = (
                "PAYLOAD_SUBSYSTEM_ANALYSIS"
                if actual_payload_provenance == "DERIVED"
                else "USER_CONFIGURED_INPUT"
            )
            assumptions.append(
                f"Payload electrical load set to {actual_payload_w:.1f} W "
                f"(Provenance: {actual_payload_provenance}, source: {actual_payload_source})."
            )
        else:
            actual_payload_w = DEFAULT_PAYLOAD_POWER_W
            actual_payload_provenance = "CONFIGURABLE_ASSUMPTION"
            actual_payload_source = f"DEFAULT_CONFIGURABLE_FALLBACK ({DEFAULT_PAYLOAD_POWER_W:.1f}W)"
            assumptions.append(
                f"Payload electrical load defaulted to {DEFAULT_PAYLOAD_POWER_W:.1f} W "
                f"(CONFIGURABLE_ASSUMPTION: standard unpowered payload)."
            )

        # Resolve reserve fraction provenance
        actual_reserve_provenance = reserve_fraction_provenance or (
            "PROJECT_REQUIREMENT"
            if abs(reserve_fraction - DEFAULT_RESERVE_FRACTION) < 1e-6
            else "CONFIGURABLE_ASSUMPTION"
        )
        assumptions.append(
            f"Reserve energy fraction set to {reserve_fraction*100.0:.1f}% "
            f"(Provenance: {actual_reserve_provenance}, source: electrical_constraints.min_reserve_energy_fraction)."
        )

        # Resolve usable fraction (DoD) provenance
        actual_usable_provenance = usable_fraction_provenance or "CONFIGURABLE_ASSUMPTION"
        assumptions.append(
            f"Maximum usable DoD fraction set to {usable_fraction*100.0:.1f}% "
            f"(Provenance: {actual_usable_provenance}: cell longevity heuristic)."
        )

        # 2. Extract authoritative Hover metrics from Phase 2
        p_hover_elec = 0.0
        hover_source = "DEFAULT_ESTIMATE"
        if hover_result is not None:
            # Sourced from AuthoritativeHoverResult
            p_hov_val = getattr(hover_result, "hover_electrical_power_w", None)
            if p_hov_val is not None and p_hov_val > 0.0:
                p_hover_elec = float(p_hov_val)
                hover_source = "PHASE_2_HOVER_MODEL"
            else:
                # Nested in authoritative_result
                auth_hov = getattr(hover_result, "authoritative_result", None)
                if auth_hov is not None and getattr(auth_hov, "hover_electrical_power_w", None):
                    p_hover_elec = float(auth_hov.hover_electrical_power_w)
                    hover_source = "PHASE_2_HOVER_MODEL"

        if p_hover_elec <= 0.0:
            # Fallback estimation if Phase 2 not run or provided
            p_hover_elec = aircraft_weight_n * 1.20 * math.sqrt(aircraft_weight_n * 1.20 / (2.0 * 1.225 * 0.5)) / 0.85
            hover_source = "HOVER_FALLBACK_ESTIMATE"
            assumptions.append("Hover electrical power estimated via momentum theory default fallback.")

        # 3. Extract authoritative Transition metrics from Phase 3
        # Forward transition (TRANSITION_TO_CRUISE)
        e_trans_fwd_wh = 0.0
        p_trans_fwd_peak_w = 0.0
        t_trans_fwd_s = 15.0
        trans_fwd_source = "DEFAULT_ESTIMATE"

        if transition_result is not None:
            auth_trans = getattr(transition_result, "authoritative_result", transition_result)
            e_kwh = getattr(auth_trans, "total_energy_kwh", None)
            if e_kwh is not None:
                e_trans_fwd_wh = float(e_kwh) * 1000.0
                trans_fwd_source = "PHASE_3_TRANSITION_MODEL"
            p_peak = getattr(auth_trans, "peak_electrical_power_w", None)
            if p_peak is not None and p_peak > 0.0:
                p_trans_fwd_peak_w = float(p_peak)
            t_s = getattr(auth_trans, "transition_duration_s", None)
            if t_s is not None and t_s > 0.0:
                t_trans_fwd_s = float(t_s)

        if e_trans_fwd_wh <= 0.0:
            # Estimate only if Phase 3 not provided
            t_trans_fwd_s = 15.0
            p_trans_fwd_peak_w = p_hover_elec * 1.10
            e_trans_fwd_wh = (p_hover_elec * 0.80) * (t_trans_fwd_s / 3600.0)
            trans_fwd_source = "TRANSITION_FALLBACK_ESTIMATE"
            assumptions.append("Forward transition energy estimated without Phase 3 corridor integration.")

        # Reverse transition (TRANSITION_TO_VTOL)
        e_trans_rev_wh = 0.0
        p_trans_rev_peak_w = 0.0
        t_trans_rev_s = t_trans_fwd_s
        trans_rev_source = "DEFAULT_ESTIMATE"

        if reverse_transition_result is not None:
            auth_rev = getattr(reverse_transition_result, "authoritative_result", reverse_transition_result)
            e_kwh = getattr(auth_rev, "total_energy_kwh", None)
            if e_kwh is not None:
                e_trans_rev_wh = float(e_kwh) * 1000.0
                trans_rev_source = "PHASE_3_TRANSITION_MODEL"
            p_peak = getattr(auth_rev, "peak_electrical_power_w", None)
            if p_peak is not None and p_peak > 0.0:
                p_trans_rev_peak_w = float(p_peak)
            t_s = getattr(auth_rev, "transition_duration_s", None)
            if t_s is not None and t_s > 0.0:
                t_trans_rev_s = float(t_s)
        else:
            # Deceleration reverse transition has similar energy profile to forward transition
            e_trans_rev_wh = e_trans_fwd_wh
            p_trans_rev_peak_w = p_trans_fwd_peak_w
            trans_rev_source = trans_fwd_source
            assumptions.append("Reverse transition energy modeled using forward transition corridor profile.")

        # 4. Extract authoritative Cruise Propulsion metrics
        p_cruise_elec = 0.0
        cruise_source = "DEFAULT_ESTIMATE"
        if cruise_propulsion_power_w is not None and cruise_propulsion_power_w > 0.0:
            p_cruise_elec = float(cruise_propulsion_power_w)
            cruise_source = "FIXED_WING_ADAPTER"
        else:
            # Default level cruise power estimate (~120 W/kg * payload or typical L/D=12)
            p_cruise_elec = (aircraft_weight_n / 12.0) * (80.0 / 3.6) / 0.75
            cruise_source = "CRUISE_FALLBACK_ESTIMATE"
            assumptions.append("Forward cruise power estimated using nominal L/D=12 and 75% propulsive efficiency.")

        # Loiter Propulsion metrics
        p_loiter_elec = 0.0
        loiter_source = "DEFAULT_ESTIMATE"
        if loiter_propulsion_power_w is not None and loiter_propulsion_power_w > 0.0:
            p_loiter_elec = float(loiter_propulsion_power_w)
            loiter_source = "FIXED_WING_ADAPTER"
        else:
            # Explicit documented engineering assumption: Loiter operates near minimum power speed
            # Minimum power for jet/prop is approx (1/sqrt(3))^0.5 to 0.88 of cruise power;
            # here we document exact equality or conservative cruise power assumption.
            p_loiter_elec = p_cruise_elec
            loiter_source = "FIXED_WING_ADAPTER_LOITER_ASSUMPTION"
            assumptions.append("Mission loiter electrical power assumed equal to level cruise electrical power (no separate fixed-wing loiter polar supplied).")

        # 5. Extract or construct Mission Profile Sequence durations
        if mission_profile_sequence is None:
            profile_seq = VTOLMissionProfileSequence.build_default_sequence()
        else:
            profile_seq = mission_profile_sequence

        durations: Dict[VTOLMissionPhase, float] = {}
        for seg in profile_seq.segments:
            durations[seg.phase] = seg.duration_s

        # Apply custom duration overrides if provided
        if custom_segment_durations_s:
            for ph, d in custom_segment_durations_s.items():
                durations[ph] = d

        # Use Phase 3 transition durations if available
        durations[VTOLMissionPhase.TRANSITION_TO_CRUISE] = t_trans_fwd_s
        durations[VTOLMissionPhase.TRANSITION_TO_VTOL] = t_trans_rev_s

        # 6. Construct 10-Phase Mission Energy Ledger
        segments: List[MissionEnergySegment] = []

        # (1) GROUND_PREFLIGHT
        t_1 = durations.get(VTOLMissionPhase.GROUND_PREFLIGHT, 60.0)
        p_av_1 = actual_avionics_w
        p_pay_1 = actual_payload_w
        p_avg_1 = p_av_1 + p_pay_1
        e_1 = p_avg_1 * t_1 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.GROUND_PREFLIGHT,
            duration_s=t_1,
            average_power_w=p_avg_1,
            peak_power_w=p_avg_1,
            energy_wh=e_1,
            propulsion_power_w=0.0,
            avionics_power_w=p_av_1,
            payload_power_w=p_pay_1,
            power_source="BATTERY",
            calculation_source="AVIONICS_SUBSYSTEM_ANALYSIS" if actual_avionics_provenance == "DERIVED" else "AVIONICS_AUXILIARY",
            load_type="AVIONICS_ONLY",
            status="IMPLEMENTED",
            notes=["Preflight avionics and ground check; propulsion systems OFF."]
        ))

        # (2) VTOL_TAKEOFF
        t_2 = durations.get(VTOLMissionPhase.VTOL_TAKEOFF, 15.0)
        p_prop_2 = p_hover_elec
        p_avg_2 = p_prop_2 + actual_avionics_w + actual_payload_w
        p_peak_2 = p_prop_2 * 1.05 + actual_avionics_w + actual_payload_w
        e_2 = p_avg_2 * t_2 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.VTOL_TAKEOFF,
            duration_s=t_2,
            average_power_w=p_avg_2,
            peak_power_w=p_peak_2,
            energy_wh=e_2,
            propulsion_power_w=p_prop_2,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=hover_source,
            load_type="PROPULSION_AND_AVIONICS",
            status="IMPLEMENTED",
            notes=["Vertical liftoff to ground effect boundary."]
        ))

        # (3) HOVER_CLIMB
        t_3 = durations.get(VTOLMissionPhase.HOVER_CLIMB, 45.0)
        p_prop_3 = p_hover_elec
        p_avg_3 = p_prop_3 + actual_avionics_w + actual_payload_w
        p_peak_3 = p_avg_3
        e_3 = p_avg_3 * t_3 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.HOVER_CLIMB,
            duration_s=t_3,
            average_power_w=p_avg_3,
            peak_power_w=p_peak_3,
            energy_wh=e_3,
            propulsion_power_w=p_prop_3,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=hover_source,
            load_type="PROPULSION_AND_AVIONICS",
            status="IMPLEMENTED",
            notes=["Vertical climbout to transition conversion altitude."]
        ))

        # (4) TRANSITION_TO_CRUISE
        t_4 = durations.get(VTOLMissionPhase.TRANSITION_TO_CRUISE, t_trans_fwd_s)
        e_aux_4 = (actual_avionics_w + actual_payload_w) * t_4 / 3600.0
        e_4 = e_trans_fwd_wh + e_aux_4
        p_prop_avg_4 = (e_trans_fwd_wh * 3600.0 / t_4) if t_4 > 0.0 else 0.0
        p_avg_4 = (e_4 * 3600.0 / t_4) if t_4 > 0.0 else 0.0
        p_peak_4 = p_trans_fwd_peak_w + actual_avionics_w + actual_payload_w
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.TRANSITION_TO_CRUISE,
            duration_s=t_4,
            average_power_w=p_avg_4,
            peak_power_w=p_peak_4,
            energy_wh=e_4,
            propulsion_power_w=p_prop_avg_4,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=trans_fwd_source,
            load_type="DUAL_BUS_BLENDED",
            status="IMPLEMENTED",
            notes=["Integrated trapezoidal energy from Phase 3 transition flight corridor."]
        ))

        # (5) FIXED_WING_CRUISE
        t_5 = durations.get(VTOLMissionPhase.FIXED_WING_CRUISE, 1200.0)
        p_prop_5 = p_cruise_elec
        p_avg_5 = p_prop_5 + actual_avionics_w + actual_payload_w
        p_peak_5 = p_avg_5
        e_5 = p_avg_5 * t_5 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.FIXED_WING_CRUISE,
            duration_s=t_5,
            average_power_w=p_avg_5,
            peak_power_w=p_peak_5,
            energy_wh=e_5,
            propulsion_power_w=p_prop_5,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=cruise_source,
            load_type="PROPULSION_AND_AVIONICS",
            status="IMPLEMENTED",
            notes=["Level wing-borne forward cruise (lift rotors locked and off)."]
        ))

        # (6) MISSION_LOITER
        t_6 = durations.get(VTOLMissionPhase.MISSION_LOITER, 300.0)
        p_prop_6 = p_loiter_elec
        p_avg_6 = p_prop_6 + actual_avionics_w + actual_payload_w
        p_peak_6 = p_avg_6
        e_6 = p_avg_6 * t_6 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.MISSION_LOITER,
            duration_s=t_6,
            average_power_w=p_avg_6,
            peak_power_w=p_peak_6,
            energy_wh=e_6,
            propulsion_power_w=p_prop_6,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=loiter_source,
            load_type="PROPULSION_AND_AVIONICS",
            status="IMPLEMENTED",
            notes=["On-station observation or surveillance loiter sweep."]
        ))

        # (7) TRANSITION_TO_VTOL
        t_7 = durations.get(VTOLMissionPhase.TRANSITION_TO_VTOL, t_trans_rev_s)
        e_aux_7 = (actual_avionics_w + actual_payload_w) * t_7 / 3600.0
        e_7 = e_trans_rev_wh + e_aux_7
        p_prop_avg_7 = (e_trans_rev_wh * 3600.0 / t_7) if t_7 > 0.0 else 0.0
        p_avg_7 = (e_7 * 3600.0 / t_7) if t_7 > 0.0 else 0.0
        p_peak_7 = p_trans_rev_peak_w + actual_avionics_w + actual_payload_w
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.TRANSITION_TO_VTOL,
            duration_s=t_7,
            average_power_w=p_avg_7,
            peak_power_w=p_peak_7,
            energy_wh=e_7,
            propulsion_power_w=p_prop_avg_7,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=trans_rev_source,
            load_type="DUAL_BUS_BLENDED",
            status="IMPLEMENTED",
            notes=["Deceleration and wing-unloading handover to vertical lift rotors."]
        ))

        # (8) HOVER_DESCENT
        t_8 = durations.get(VTOLMissionPhase.HOVER_DESCENT, 45.0)
        p_prop_8 = p_hover_elec
        p_avg_8 = p_prop_8 + actual_avionics_w + actual_payload_w
        p_peak_8 = p_avg_8
        e_8 = p_avg_8 * t_8 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.HOVER_DESCENT,
            duration_s=t_8,
            average_power_w=p_avg_8,
            peak_power_w=p_peak_8,
            energy_wh=e_8,
            propulsion_power_w=p_prop_8,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=hover_source,
            load_type="PROPULSION_AND_AVIONICS",
            status="IMPLEMENTED",
            notes=["Controlled vertical descent over recovery pad."]
        ))

        # (9) VTOL_LANDING
        t_9 = durations.get(VTOLMissionPhase.VTOL_LANDING, 15.0)
        p_prop_9 = p_hover_elec
        p_avg_9 = p_prop_9 + actual_avionics_w + actual_payload_w
        p_peak_9 = p_avg_9
        e_9 = p_avg_9 * t_9 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.VTOL_LANDING,
            duration_s=t_9,
            average_power_w=p_avg_9,
            peak_power_w=p_peak_9,
            energy_wh=e_9,
            propulsion_power_w=p_prop_9,
            avionics_power_w=actual_avionics_w,
            payload_power_w=actual_payload_w,
            power_source="BATTERY",
            calculation_source=hover_source,
            load_type="PROPULSION_AND_AVIONICS",
            status="IMPLEMENTED",
            notes=["Touchdown, ground contact detection, and rotor spin-down."]
        ))

        # (10) GROUND_POSTFLIGHT
        t_10 = durations.get(VTOLMissionPhase.GROUND_POSTFLIGHT, 30.0)
        p_av_10 = actual_avionics_w
        p_pay_10 = actual_payload_w
        p_avg_10 = p_av_10 + p_pay_10
        e_10 = p_avg_10 * t_10 / 3600.0
        segments.append(MissionEnergySegment(
            phase=VTOLMissionPhase.GROUND_POSTFLIGHT,
            duration_s=t_10,
            average_power_w=p_avg_10,
            peak_power_w=p_avg_10,
            energy_wh=e_10,
            propulsion_power_w=0.0,
            avionics_power_w=p_av_10,
            payload_power_w=p_pay_10,
            power_source="BATTERY",
            calculation_source="AVIONICS_SUBSYSTEM_ANALYSIS" if actual_avionics_provenance == "DERIVED" else "AVIONICS_AUXILIARY",
            load_type="AVIONICS_ONLY",
            status="IMPLEMENTED",
            notes=["Postflight telemetry flush, log writing, and safe disarm."]
        ))

        # 7. Energy Ledger Totals and Conservation Invariants
        total_duration_s = sum(s.duration_s for s in segments)
        total_prop_energy_wh = sum(
            (s.energy_wh - (s.avionics_power_w + s.payload_power_w) * s.duration_s / 3600.0)
            if s.load_type in ("PROPULSION_AND_AVIONICS", "DUAL_BUS_BLENDED", "PROPULSION_ONLY") else 0.0
            for s in segments
        )
        total_av_energy_wh = sum(s.avionics_power_w * s.duration_s / 3600.0 for s in segments)
        total_pay_energy_wh = sum(s.payload_power_w * s.duration_s / 3600.0 for s in segments)
        total_mission_energy_wh = sum(s.energy_wh for s in segments)

        # Validate ledger invariants
        ledger_msgs: List[str] = []
        has_double_count = False
        is_complete = True

        expected_phases = set(VTOLMissionPhase)
        found_phases = set(s.phase for s in segments)
        if found_phases != expected_phases:
            is_complete = False
            missing = expected_phases - found_phases
            ledger_msgs.append(f"Missing mission phases from ledger: {[p.value for p in missing]}")

        # Check for duplicates
        if len(segments) != len(set(s.phase for s in segments)):
            has_double_count = True
            ledger_msgs.append("Duplicate mission phases detected in ledger sequence.")

        for s in segments:
            if s.duration_s < 0.0:
                ledger_msgs.append(f"Negative duration in phase {s.phase.value}: {s.duration_s}s.")
            if s.average_power_w < 0.0 or s.peak_power_w < 0.0:
                ledger_msgs.append(f"Negative power in phase {s.phase.value}.")
            if s.energy_wh < 0.0:
                ledger_msgs.append(f"Negative energy in phase {s.phase.value}.")

        # Check exact energy summation conservation
        sum_check = sum(s.energy_wh for s in segments)
        if abs(sum_check - total_mission_energy_wh) > 1e-6:
            ledger_msgs.append(f"Energy conservation mismatch: sum={sum_check:.6f} Wh, total={total_mission_energy_wh:.6f} Wh.")

        if ledger_msgs and any("Negative" in m or "Duplicate" in m for m in ledger_msgs):
            raise EnergyLedgerValidationError(ledger_msgs)

        ledger = MissionEnergyLedger(
            segments=segments,
            total_mission_duration_s=total_duration_s,
            total_propulsion_energy_wh=total_prop_energy_wh,
            total_avionics_energy_wh=total_av_energy_wh,
            total_payload_energy_wh=total_pay_energy_wh,
            total_mission_energy_wh=total_mission_energy_wh,
            is_complete=is_complete,
            has_double_counting=has_double_count,
            status="IMPLEMENTED" if is_complete and not has_double_count else "PARTIAL",
            validation_messages=ledger_msgs
        )

        # 8. Battery Energy & Capacity Sizing
        reserve_energy_wh = total_mission_energy_wh * reserve_fraction
        req_usable_energy_wh = total_mission_energy_wh + reserve_energy_wh
        req_nominal_battery_energy_wh = req_usable_energy_wh / usable_fraction

        req_usable_cap_ah: Optional[float] = None
        req_nominal_cap_ah: Optional[float] = None
        if system_voltage_v is not None and system_voltage_v > 0.0:
            req_usable_cap_ah = req_usable_energy_wh / system_voltage_v
            req_nominal_cap_ah = req_nominal_battery_energy_wh / system_voltage_v
        else:
            warnings.append("System voltage is undefined; required Amp-hour capacity cannot be resolved.")

        # Battery Mass Interface (Phase 5 boundary)
        est_batt_mass_kg: Optional[float] = None
        batt_mass_status = "UNRESOLVED_DEFERRED_TO_PHASE5"
        if specific_energy_wh_kg is not None and specific_energy_wh_kg > 0.0:
            est_batt_mass_kg = req_nominal_battery_energy_wh / specific_energy_wh_kg
            batt_mass_status = "ESTIMATED_FROM_SPECIFIC_ENERGY"
            assumptions.append(f"Battery mass estimated using explicit specific energy {specific_energy_wh_kg:.1f} Wh/kg.")
        else:
            assumptions.append("Battery mass is unresolved in Phase 4 and intentionally deferred to Phase 5 MTOW convergence.")

        battery_sizing = BatterySizingRequirements(
            mission_energy_wh=total_mission_energy_wh,
            reserve_fraction=reserve_fraction,
            reserve_energy_wh=reserve_energy_wh,
            required_usable_energy_wh=req_usable_energy_wh,
            usable_fraction=usable_fraction,
            required_nominal_battery_energy_wh=req_nominal_battery_energy_wh,
            nominal_voltage_v=system_voltage_v,
            required_usable_capacity_ah=req_usable_cap_ah,
            required_nominal_capacity_ah=req_nominal_cap_ah,
            specific_energy_wh_kg=specific_energy_wh_kg,
            estimated_battery_mass_kg=est_batt_mass_kg,
            battery_mass_status=batt_mass_status,
            status="IMPLEMENTED" if system_voltage_v is not None else "PARTIAL",
            engineering_assumptions=assumptions,
            warnings=warnings,
        )

        # 9. Electrical Power & Current Envelope
        mission_avg_power_w = (total_mission_energy_wh * 3600.0 / total_duration_s) if total_duration_s > 0.0 else 0.0

        # Maximum continuous power (typically sustained hover or sustained cruise)
        p_cruise_cont = p_cruise_elec + actual_avionics_w + actual_payload_w
        p_hover_cont = p_hover_elec + actual_avionics_w + actual_payload_w
        max_cont_power_w = max(p_cruise_cont, p_hover_cont)

        # Maximum peak power (typically simultaneous transition load or takeoff)
        max_peak_power_w = max(s.peak_power_w for s in segments)

        # Transition simultaneous power
        trans_seg = ledger.get_segment(VTOLMissionPhase.TRANSITION_TO_CRUISE)
        simult_trans_power_w = trans_seg.peak_power_w if trans_seg else max_peak_power_w

        # Currents & C-rates if voltage is available
        cont_curr_a: Optional[float] = None
        peak_curr_a: Optional[float] = None
        simult_trans_curr_a: Optional[float] = None
        cont_c_rate: Optional[float] = None
        peak_c_rate: Optional[float] = None
        is_c_rate_compliant: Optional[bool] = None

        if system_voltage_v is not None and system_voltage_v > 0.0:
            cont_curr_a = max_cont_power_w / system_voltage_v
            peak_curr_a = max_peak_power_w / system_voltage_v
            simult_trans_curr_a = simult_trans_power_w / system_voltage_v

            if req_nominal_cap_ah is not None and req_nominal_cap_ah > 0.0:
                cont_c_rate = cont_curr_a / req_nominal_cap_ah
                peak_c_rate = peak_curr_a / req_nominal_cap_ah

                if max_allowable_c_rate is not None and max_allowable_c_rate > 0.0:
                    is_c_rate_compliant = peak_c_rate <= max_allowable_c_rate
                    if not is_c_rate_compliant:
                        warnings.append(
                            f"Peak C-rate ({peak_c_rate:.2f} C) exceeds configured allowable limit "
                            f"({max_allowable_c_rate:.2f} C)."
                        )

        # 10. Electrical Buses
        lift_curr_cont: Optional[float] = (p_hover_elec / system_voltage_v) if (system_voltage_v and system_voltage_v > 0) else None
        lift_curr_per_motor: Optional[float] = (lift_curr_cont / lift_motor_count) if (lift_curr_cont and lift_motor_count > 0) else None

        lift_bus = ElectricalBusMetrics(
            bus_name="Lift Propulsion High-Voltage Bus",
            continuous_power_w=p_hover_elec,
            peak_power_w=p_hover_elec * 1.10,
            continuous_current_a=lift_curr_cont,
            peak_current_a=lift_curr_cont * 1.10 if lift_curr_cont else None,
            motor_count=lift_motor_count,
            per_motor_current_a=lift_curr_per_motor,
            subsystems_connected=[f"{lift_motor_count}x Vertical Lift Motors", f"{lift_motor_count}x Lift ESCs"]
        )

        cruise_curr: Optional[float] = (p_cruise_elec / system_voltage_v) if (system_voltage_v and system_voltage_v > 0) else None
        cruise_bus = ElectricalBusMetrics(
            bus_name="Cruise Propulsion High-Voltage Bus",
            continuous_power_w=p_cruise_elec,
            peak_power_w=p_cruise_elec * 1.25,
            continuous_current_a=cruise_curr,
            peak_current_a=cruise_curr * 1.25 if cruise_curr else None,
            motor_count=1,
            per_motor_current_a=cruise_curr,
            subsystems_connected=["1x Forward Cruise Motor", "1x Forward ESC"]
        )

        avionics_curr: Optional[float] = ((actual_avionics_w + actual_payload_w) / 5.0)  # Standard 5V BEC rail
        avionics_bus = ElectricalBusMetrics(
            bus_name="Avionics & Payload Low-Voltage Regulated Bus (BEC)",
            continuous_power_w=actual_avionics_w + actual_payload_w,
            peak_power_w=(actual_avionics_w + actual_payload_w) * 1.5,
            continuous_current_a=avionics_curr,
            peak_current_a=avionics_curr * 1.5 if avionics_curr else None,
            motor_count=0,
            per_motor_current_a=None,
            subsystems_connected=["Autopilot Flight Controller", "Sensors & IMU Suite", "Radio & Telemetry", "Payload Bay"]
        )

        envelope = ElectricalEnvelope(
            mission_average_power_w=mission_avg_power_w,
            maximum_continuous_power_w=max_cont_power_w,
            maximum_peak_power_w=max_peak_power_w,
            continuous_current_a=cont_curr_a,
            peak_current_a=peak_curr_a,
            continuous_c_rate=cont_c_rate,
            peak_c_rate=peak_c_rate,
            c_rate_limit=max_allowable_c_rate,
            is_c_rate_compliant=is_c_rate_compliant,
            lift_bus=lift_bus,
            cruise_bus=cruise_bus,
            avionics_bus=avionics_bus,
            simultaneous_transition_power_w=simult_trans_power_w,
            simultaneous_transition_current_a=simult_trans_curr_a,
            status="IMPLEMENTED" if system_voltage_v is not None else "PARTIAL"
        )

        overall_status = "IMPLEMENTED"
        if system_voltage_v is None:
            overall_status = "PARTIAL"

        # 11. Compile Comprehensive Parameter Provenance Matrix
        parameter_provenance: Dict[str, Dict[str, Any]] = {
            "hover_electrical_power_w": {
                "value": round(p_hover_elec, 2),
                "classification": "DERIVED" if hover_source == "PHASE_2_HOVER_MODEL" else "CONFIGURABLE_ASSUMPTION",
                "provenance_source": hover_source,
                "notes": "Phase 2 AuthoritativeHoverModel momentum theory & rotor disk area."
            },
            "transition_energy_wh": {
                "value": round(e_trans_fwd_wh, 3),
                "classification": "DERIVED" if trans_fwd_source == "PHASE_3_TRANSITION_MODEL" else "CONFIGURABLE_ASSUMPTION",
                "provenance_source": trans_fwd_source,
                "notes": "Phase 3 AuthoritativeTransitionModel flight corridor numerical integration."
            },
            "cruise_electrical_power_w": {
                "value": round(p_cruise_elec, 2),
                "classification": "DERIVED" if cruise_source == "FIXED_WING_ADAPTER" else "CONFIGURABLE_ASSUMPTION",
                "provenance_source": cruise_source,
                "notes": "Fixed-Wing backend cruise propulsion shaft power / motor efficiency."
            },
            "avionics_power_w": {
                "value": round(actual_avionics_w, 2),
                "classification": actual_avionics_provenance,
                "provenance_source": actual_avionics_source,
                "notes": "Autopilot, telemetry, sensors, and BEC auxiliary load."
            },
            "payload_power_w": {
                "value": round(actual_payload_w, 2),
                "classification": actual_payload_provenance,
                "provenance_source": actual_payload_source,
                "notes": "Payload sensor and gimbal stabilization power draw."
            },
            "reserve_fraction": {
                "value": round(reserve_fraction, 4),
                "classification": actual_reserve_provenance,
                "provenance_source": "electrical_constraints.min_reserve_energy_fraction" if reserve_fraction == DEFAULT_RESERVE_FRACTION else "USER_CONFIGURED_OVERRIDE",
                "notes": "Reserve battery energy buffer (Torq Wings project requirement: min 20%)."
            },
            "usable_dod_fraction": {
                "value": round(usable_fraction, 4),
                "classification": "CONFIGURABLE_ASSUMPTION",
                "provenance_source": "DEFAULT_USABLE_DOD_FRACTION" if usable_fraction == DEFAULT_USABLE_DOD_FRACTION else "USER_CONFIGURED_OVERRIDE",
                "notes": "Maximum allowable depth of discharge to protect cell cycle longevity."
            },
            "specific_energy_wh_kg": {
                "value": round(specific_energy_wh_kg, 2) if specific_energy_wh_kg else None,
                "classification": "CONFIGURABLE_ASSUMPTION" if specific_energy_wh_kg else "DEFERRED",
                "provenance_source": "BATTERY_CHEMISTRY_TABLE" if specific_energy_wh_kg else "DEFERRED_TO_PHASE5",
                "notes": "Gravimetric energy density for preliminary battery mass sizing."
            },
            "battery_mass_convergence": {
                "value": None,
                "classification": "DEFERRED",
                "provenance_source": "DEFERRED_TO_PHASE5",
                "notes": "Multidisciplinary structural mass synthesis & closed-loop MTOW iteration."
            }
        }

        return AuthoritativeEnergyResult(
            sizing_mass_kg=sizing_mass_kg,
            aircraft_weight_n=aircraft_weight_n,
            lift_motor_count=lift_motor_count,
            ledger=ledger,
            battery_sizing=battery_sizing,
            envelope=envelope,
            is_converged_mtow=False,
            mtow_status="PRE_CONVERGENCE_SIZING",
            status=overall_status,
            engineering_assumptions=assumptions,
            parameter_provenance=parameter_provenance,
            warnings=warnings,
            errors=errors,
            metadata={
                "hover_source": hover_source,
                "transition_fwd_source": trans_fwd_source,
                "transition_rev_source": trans_rev_source,
                "cruise_source": cruise_source,
                "loiter_source": loiter_source,
                "avionics_source": actual_avionics_source,
                "payload_source": actual_payload_source,
            }
        )
