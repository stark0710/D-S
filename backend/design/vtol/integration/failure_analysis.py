"""
VTOL Phase 9 Failure-Mode Analysis (FMEA) Engine.

Purpose:
    Performs preliminary system-level failure modes and effects analysis (FMEA)
    evaluating 13 mandatory failure scenarios across multirotor hover, transition,
    and fixed-wing cruise flight regimes.

Standards:
    - Never claims safe controllability without analytical establishment.
    - Explicitly utilizes ControllabilityStatus (VERIFIED, DEFERRED, INSUFFICIENT_INPUT, NOT_ANALYZED).
    - Preserves rigorous aerospace safety taxonomy.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .integration_models import (
    ControllabilityStatus,
    FailureModeResult,
    MissionState,
    ProvenanceCategory,
    VerificationCheckStatus,
)


class FailureAnalysisEngine:
    """
    Evaluates system mitigation and controllability across 13 required failure modes.
    """

    @classmethod
    def evaluate_failure_modes(cls) -> List[FailureModeResult]:
        """
        Synthesizes the complete 13-mode FMEA table.
        """
        fmea_records: List[FailureModeResult] = [
            # 1. Single VTOL motor failure
            FailureModeResult(
                failure_id="FMEA-01",
                failure_mode="Single VTOL Lift Motor Failure (Loss of 1 of 4 lift rotors)",
                affected_subsystem="VTOL Propulsion (T-Motor MN4014)",
                mission_states_affected=[
                    MissionState.VTOL_TAKEOFF,
                    MissionState.HOVER_CLIMB,
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.TRANSITION_TO_VTOL,
                    MissionState.HOVER_DESCENT,
                    MissionState.VTOL_LANDING,
                ],
                severity="CRITICAL",
                existing_mitigation=(
                    "In Fixed-Wing Cruise: No effect (lift motors stopped). "
                    "In Transition: Immediate abort to forward fixed-wing gliding mode using cruise pusher and aerodynamic surfaces. "
                    "In Pure Hover: Quadrotor configuration cannot maintain roll/pitch equilibrium with 3 motors without specialized spinning recovery."
                ),
                required_autopilot_response="Immediate full forward throttle to gain airspeed if above stall, or parachute deployment / controlled descent.",
                controllability_status=ControllabilityStatus.DEFERRED,
                verification_status=VerificationCheckStatus.WARNING,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Controllability in pure hover with 1 motor out is DEFERRED: QuadPlane requires aerodynamic forward speed or ballistic recovery.",
            ),

            # 2. Single VTOL ESC failure
            FailureModeResult(
                failure_id="FMEA-02",
                failure_mode="Single VTOL ESC Failure / DShot Signal Loss",
                affected_subsystem="VTOL Electrical Drive (T-Motor AIR 40A ESC)",
                mission_states_affected=[
                    MissionState.VTOL_TAKEOFF,
                    MissionState.HOVER_CLIMB,
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.TRANSITION_TO_VTOL,
                    MissionState.HOVER_DESCENT,
                    MissionState.VTOL_LANDING,
                ],
                severity="CRITICAL",
                existing_mitigation="Identical to single motor failure. DShot telemetry packet timeout flags ESC failure to Pixhawk within 50ms.",
                required_autopilot_response="ArduPilot EKF emergency action: forward pitch and cruise thrust acceleration to transition into wing-borne flight.",
                controllability_status=ControllabilityStatus.DEFERRED,
                verification_status=VerificationCheckStatus.WARNING,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Hover controllability is DEFERRED; forward recovery depends on altitude and airspeed margin.",
            ),

            # 3. Cruise motor failure
            FailureModeResult(
                failure_id="FMEA-03",
                failure_mode="Cruise Motor Failure (Pusher Motor Flameout / Mechanical Seizure)",
                affected_subsystem="Cruise Propulsion (T-Motor AT2820)",
                mission_states_affected=[
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                ],
                severity="MAJOR",
                existing_mitigation=(
                    "4x VTOL lift rotors remain fully functional and independent. "
                    "Aircraft can execute transition back to VTOL hover mode or perform aerodynamic fixed-wing glide to spot landing."
                ),
                required_autopilot_response="Autopilot detects loss of forward acceleration; initiates emergency inbound transition to QuadPlane hover landing at nearest safe coordinate.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: dual independent propulsion architecture enables lift rotors to take over; dynamic recovery profile requires flight-test demonstration.",
            ),

            # 4. Cruise ESC failure
            FailureModeResult(
                failure_id="FMEA-04",
                failure_mode="Cruise ESC Failure / Throttle Loss",
                affected_subsystem="Cruise Electrical Drive (Hobbywing FlyFun 40A)",
                mission_states_affected=[
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                ],
                severity="MAJOR",
                existing_mitigation="Identical to cruise motor failure. Lift propulsion bus and autopilot remain independently powered.",
                required_autopilot_response="Command emergency VTOL transition and vertical touchdown.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: multicopter recovery supported by architecture but unvalidated dynamically.",
            ),

            # 5. GNSS loss
            FailureModeResult(
                failure_id="FMEA-05",
                failure_mode="Loss of GNSS 3D Fix / RTK Glitch / Jamming",
                affected_subsystem="Navigation System (Holybro H-RTK F9P)",
                mission_states_affected=[
                    MissionState.HOVER_CLIMB,
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                    MissionState.TRANSITION_TO_VTOL,
                    MissionState.HOVER_DESCENT,
                ],
                severity="MAJOR",
                existing_mitigation="EKF3 sensor fusion falls back to dead reckoning using triple IMU accelerometers, gyros, compass, and digital airspeed sensor.",
                required_autopilot_response="Switch flight mode to ALT_HOLD / QSTABILIZE; command pilot manual takeover via RC or circle loiter while awaiting GNSS recovery.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: ArduPilot EKF3 dead-reckoning fallback handles attitude; position drift requires pilot or visual aiding.",
            ),

            # 6. Airspeed sensor loss
            FailureModeResult(
                failure_id="FMEA-06",
                failure_mode="Airspeed Pitot Clogging / I2C Bus Fault (ASPD-4525)",
                affected_subsystem="Air Data System (Matek ASPD-4525)",
                mission_states_affected=[
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                    MissionState.TRANSITION_TO_VTOL,
                ],
                severity="MAJOR",
                existing_mitigation="ArduPilot ARSPD_USE failover: automatically calculates synthetic airspeed from GNSS groundspeed and wind estimation.",
                required_autopilot_response="Autopilot disables faulty pitot readings; uses synthetic airspeed and increases cruise throttle margin by +15% to prevent stall.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: synthetic airspeed fallback algorithmically mitigates pitot failure; aero-calibrated proof unperformed.",
            ),

            # 7. RC link loss
            FailureModeResult(
                failure_id="FMEA-07",
                failure_mode="RC Control Link Loss / Receiver Antenna Detachment",
                affected_subsystem="Radio Control Link (TBS Crossfire Nano)",
                mission_states_affected=[
                    MissionState.HOVER_CLIMB,
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                    MissionState.TRANSITION_TO_VTOL,
                    MissionState.HOVER_DESCENT,
                ],
                severity="MINOR",
                existing_mitigation="Aircraft operates autonomously under ArduPilot mission scripts. Cellular/SiK 915MHz telemetry link provides secondary C2 channel.",
                required_autopilot_response="ArduPilot RC Failsafe triggered after 2.0s timeout: executes Return-to-Launch (RTL) or continues programmed mission if autonomous flag set.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: standard ArduPilot autonomous RTL failsafe policy.",
            ),

            # 8. Telemetry loss
            FailureModeResult(
                failure_id="FMEA-08",
                failure_mode="Ground Station Telemetry Loss (SiK 915MHz Radio Disconnect)",
                affected_subsystem="Ground Communications (Holybro SiK 915MHz)",
                mission_states_affected=[
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                ],
                severity="MINOR",
                existing_mitigation="RC control link remains active; onboard autopilot executes pre-loaded autonomous mission without ground station intervention.",
                required_autopilot_response="GCS failsafe timer: if no heartbeat received within configurable timeout (default 30s), vehicle can be configured to continue mission or return to home.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: telemetry loss does not impact local flight stabilization.",
            ),

            # 9. Companion computer failure
            FailureModeResult(
                failure_id="FMEA-09",
                failure_mode="Companion Computer Crash / Power Loss / Software Hang (Raspberry Pi 4B)",
                affected_subsystem="High-Level Autonomy (Raspberry Pi 4B)",
                mission_states_affected=[
                    MissionState.MISSION_LOITER,
                    MissionState.FIXED_WING_CRUISE,
                ],
                severity="MINOR",
                existing_mitigation=(
                    "Crucial architectural isolation: Pixhawk 6X autopilot runs real-time NuttX OS independently of Linux SBC. "
                    "Companion computer has zero direct connection to actuators or ESCs."
                ),
                required_autopilot_response="Pixhawk detects loss of MAVLink heartbeat from companion; drops vision-assisted waypoints and defaults to standard internal waypoint navigation.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: real-time OS isolation guarantees autopilot integrity during SBC crash.",
            ),

            # 10. Battery low-voltage condition
            FailureModeResult(
                failure_id="FMEA-10",
                failure_mode="Battery Low-Voltage Warning / Rapid Cell Depletion",
                affected_subsystem="Energy Storage (Tattu Plus 6S 22000mAh)",
                mission_states_affected=[
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                    MissionState.TRANSITION_TO_VTOL,
                ],
                severity="MAJOR",
                existing_mitigation="PDB voltage/current sensor monitors cell voltage and cumulative mAh consumed; two-stage alerts set at 21.6V (warning) and 20.4V (critical).",
                required_autopilot_response="Stage 1: Abort mission and route directly to nearest landing zone. Stage 2: Immediate VTOL descent and land.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: two-stage voltage failsafe parameter configuration in ArduPilot.",
            ),

            # 11. Power-distribution failure
            FailureModeResult(
                failure_id="FMEA-11",
                failure_mode="PDB Total Bus Short Circuit or Cold Solder Joint (Matek PDB-HEX)",
                affected_subsystem="Power Distribution (Matek PDB-HEX)",
                mission_states_affected=[
                    MissionState.VTOL_TAKEOFF,
                    MissionState.HOVER_CLIMB,
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                    MissionState.TRANSITION_TO_VTOL,
                    MissionState.HOVER_DESCENT,
                    MissionState.VTOL_LANDING,
                ],
                severity="CRITICAL",
                existing_mitigation="High-current copper busbars rated to 140A continuous; dual separated BECs isolate 5V avionics from high-voltage motor spikes.",
                required_autopilot_response="Total power loss cannot be mitigated by software; requires mechanical parachute deployment or backup battery on secondary Pixhawk power port.",
                controllability_status=ControllabilityStatus.NOT_ANALYZED,
                verification_status=VerificationCheckStatus.WARNING,
                provenance=ProvenanceCategory.PROJECT_REQUIREMENT,
                notes="Single point of failure without dual battery redundancy; secondary battery backup recommended for commercial certification.",
            ),

            # 12. Servo failure
            FailureModeResult(
                failure_id="FMEA-12",
                failure_mode="Single Servo Jam or Gear Stripping (KST DS215MG)",
                affected_subsystem="Flight Control Actuation (Aileron or Ruddervator Servo)",
                mission_states_affected=[
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.TRANSITION_TO_VTOL,
                ],
                severity="MAJOR",
                existing_mitigation=(
                    "In hover: Multirotor differential thrust provides roll, pitch, and yaw control (servos not required). "
                    "In cruise: Dual ailerons and dual inverted V-tail ruddervators provide cross-coupling redundancy; roll can be supplemented by differential lift motor thrust."
                ),
                required_autopilot_response="Trim remaining surfaces to compensate for drag/moment; transition to VTOL hover for touchdown.",
                controllability_status=ControllabilityStatus.DEFERRED,
                verification_status=VerificationCheckStatus.WARNING,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Cross-control trim authority under jammed control surface is DEFERRED to dynamic aeroelastic testing.",
            ),

            # 13. Flight-controller interface failure
            FailureModeResult(
                failure_id="FMEA-13",
                failure_mode="Flight Controller Main PWM Bus or I2C Bus Lockup",
                affected_subsystem="Autopilot Computing (Holybro Pixhawk 6X)",
                mission_states_affected=[
                    MissionState.VTOL_TAKEOFF,
                    MissionState.HOVER_CLIMB,
                    MissionState.TRANSITION_TO_CRUISE,
                    MissionState.FIXED_WING_CRUISE,
                    MissionState.MISSION_LOITER,
                    MissionState.TRANSITION_TO_VTOL,
                    MissionState.HOVER_DESCENT,
                    MissionState.VTOL_LANDING,
                ],
                severity="CRITICAL",
                existing_mitigation=(
                    "Pixhawk 6X features dual processor architecture: STM32H753 main flight management unit (FMU) + "
                    "STM32F103 dedicated I/O failover coprocessor (IOMCU) with separate watchdog timers."
                ),
                required_autopilot_response="Hardware watchdog triggers automatic IOMCU failsafe override; restores manual RC direct pass-through within 100ms.",
                controllability_status=ControllabilityStatus.CONFIGURATION_SUPPORTED,
                verification_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Configuration-supported: dual processor separation handles FMU lockup; IOMCU manual override is configuration-dependent.",
            ),
        ]

        return fmea_records

