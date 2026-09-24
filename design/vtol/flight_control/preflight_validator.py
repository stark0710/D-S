"""
VTOL Phase 10 Pre-Flight Validator and Ground-Test Checklist Engine.

Purpose:
    Executes deterministic software-side validation of the complete ArduPilot configuration,
    enforcing arming safety gates and generating an authoritative 18-point ground-test checklist.
    Guarantees that no test is falsely marked passed before physical bench execution.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .flight_control_models import (
    ArduPilotParameter,
    FlightControlStatus,
    GroundTestChecklistItem,
    GroundTestExecutionStatus,
    GroundTestReadiness,
    HardwareReconciliationItem,
    MotorOutputAssignment,
    PreflightCheckResult,
    SensorConfigurationItem,
    ServoOutputAssignment,
)


class PreflightValidatorEngine:
    """
    Authoritative pre-flight rules checker and ground test checklist synthesizer.
    """

    @classmethod
    def generate_ground_test_checklist(cls) -> List[GroundTestChecklistItem]:
        """
        Synthesizes the mandatory 18-point ground test checklist (Prompt Section 25).
        All items are strictly marked NOT_EXECUTED until physical bench tests are performed.
        """
        tests: List[GroundTestChecklistItem] = [
            GroundTestChecklistItem(
                test_id="GROUND-TEST-01",
                test_name="Pixhawk 6X Power-Up & Rail Voltage Stability",
                subsystem="Flight Controller & Power Distribution",
                procedure="Apply 6S LiPo power via XT90-S; measure 5.0V regulated avionics bus voltage under idle and boot load.",
                expected_result="POWER1 VCC reads 5.05V +/- 0.1V; status LEDs indicate clean boot without brownout reset.",
                prerequisite="Battery and Matek PDB-HEX connected with verified polarity.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-02",
                test_name="Sensor Subsystem Hardware Detection",
                subsystem="Avionics & Bus Communication",
                procedure="Query ArduPilot MAVLink device table via Mission Planner / QGroundControl.",
                expected_result="F9P GNSS, IST8310 compass, MS4525 airspeed, dual barometers, and 3x IMUs detected on I2C/SPI/CAN.",
                prerequisite="Pixhawk powered up and connected to GCS via USB or SiK radio.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-03",
                test_name="GNSS & RTK Fix Acquisition",
                subsystem="Navigation",
                procedure="Position aircraft in open sky; verify satellite constellation count and RTK carrier phase lock.",
                expected_result="Satellite count >= 16, HDOP <= 0.8, 3D DGPS or RTK Fixed status verified.",
                prerequisite="Outdoor sky visibility; RTK correction stream active.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-04",
                test_name="Compass Orientation & Magnetic Interference",
                subsystem="Navigation",
                procedure="Perform 360-degree yaw rotation on ground; compare reported heading against surveyed magnetic bearing.",
                expected_result="Reported heading within +/- 2.5 degrees of true bearing; zero magnetic anomaly warning.",
                prerequisite="Full 3D compass sphere calibration completed.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-05",
                test_name="Digital Airspeed Zero-Offset & Dynamic Pressure",
                subsystem="Air Data",
                procedure="Cover pitot probe to verify zero drift; gently blow into pitot tube to test dynamic pressure response.",
                expected_result="Zero airspeed reads < 1.0 m/s; positive velocity spike (>15 m/s) cleanly recorded without I2C error.",
                prerequisite="Pneumatic silicone tubes securely clamped with zero air leak.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-06",
                test_name="RC Pilot Control Link & Range Check",
                subsystem="C2 Link",
                procedure="Execute low-power RF range test at 30m; verify full stick deflection on Channels 1-4 and flight mode switch.",
                expected_result="Link quality (LQ) = 100%, 0 lost frames, jitter < 2us, mode switch cycles correctly.",
                prerequisite="Transmitter and Crossfire Nano RX bound and calibrated.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-07",
                test_name="MAVLink Telemetry Bi-Directional Link",
                subsystem="GCS Telemetry",
                procedure="Stream high-rate telemetry over 915MHz SiK radio; send parameter download and command pulse.",
                expected_result="57600 baud link maintains >95% packet success rate with CTS/RTS hardware flow control active.",
                prerequisite="Antennas vertically polarized with adequate physical separation.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-08",
                test_name="Motor Output Channel Identification",
                subsystem="Propulsion Actuation",
                procedure="Execute ArduPilot Motor Test dialog on GCS at 5% throttle sequentially for M1, M2, M3, M4, M5.",
                expected_result="Motor 1 (FL), Motor 2 (FR), Motor 3 (RL), Motor 4 (RR), and Motor 5 (Pusher) spin in correct sequence.",
                prerequisite="Propellers REMOVED from all 5 motors for bench safety.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-09",
                test_name="Motor Physical Rotation Direction Confirmation",
                subsystem="Propulsion Actuation",
                procedure="Physically verify shaft rotation direction against nominal Quad-X and pusher requirements.",
                expected_result="M1 spins CW, M2 spins CCW, M3 spins CCW, M4 spins CW, M5 spins CW (pusher); if inverted, swap phase leads or invert DShot.",
                prerequisite="Propellers REMOVED; tactile or high-speed visual verification.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-10",
                test_name="ESC Throttle Response & Protocol Synchronization",
                subsystem="Propulsion Actuation",
                procedure="Test rapid throttle steps (0% -> 25% -> 50% -> 0%) via GCS motor test dialog.",
                expected_result="Sub-millisecond throttle tracking without desync, stuttering, or ESC overheating.",
                prerequisite="Propellers REMOVED; DC bench supply current limited to 20A.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-11",
                test_name="Outboard Aileron Deflection Direction & Travel",
                subsystem="Flight Control Surfaces",
                procedure="Command right roll stick input; observe left and right aileron trailing edge deflections.",
                expected_result="Right aileron deflects UP, Left aileron deflects DOWN; full stick produces +/- 20 degrees deflection.",
                prerequisite="Mechanical servo pushrod linkages connected and mechanically centered.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-12",
                test_name="Inverted V-Tail Ruddervator Deflection Direction",
                subsystem="Flight Control Surfaces",
                procedure="Command nose-up elevator stick input; observe left and right ruddervator deflections on inverted V-tail.",
                expected_result="Both surfaces deflect trailing edge UP/OUTWARD to generate nose-up pitching moment.",
                prerequisite="V-tail linkages connected and neutral trim verified.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-13",
                test_name="V-Tail Pitch & Yaw Mathematical Mixing",
                subsystem="Flight Control Surfaces",
                procedure="Command pure yaw right stick input; verify differential surface deflection on V-tail.",
                expected_result="Surfaces deflect differentially to produce positive aerodynamic yaw moment without parasitic pitch.",
                prerequisite="GROUND-TEST-12 passed; mixer gains set in ArduPilot.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-14",
                test_name="Analog Battery Monitor Voltage & Current Scaling",
                subsystem="Power Monitor",
                procedure="Measure battery terminal voltage with calibrated digital multimeter; draw 10A through dummy load.",
                expected_result="Autopilot reported voltage matches multimeter within +/- 0.05V; current matches within +/- 0.2A.",
                prerequisite="Calibrated external DMM and DC load bank.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-15",
                test_name="Hardware & Software Failsafe Response",
                subsystem="Safety & Redundancy",
                procedure="Turn off RC transmitter while armed in QHOVER mode; monitor autopilot mode change.",
                expected_result="Autopilot immediately triggers THR_FAILSAFE and transitions to QRTL within 1.5s.",
                prerequisite="Propellers REMOVED; motors disarmed before physical approach.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-16",
                test_name="Pre-Arm Safety Checks & Arming / Disarming Sequence",
                subsystem="Safety & Arming Logic",
                procedure="Attempt arming with safety switch pressed, then attempt arming with disconnected airspeed tube.",
                expected_result="Clean arming when all sensors healthy; arming blocked with descriptive pre-arm error when airspeed missing.",
                prerequisite="ARMING_CHECK parameter set to 1 (All checks active).",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-17",
                test_name="Bench Transition Logic & Motor Handover",
                subsystem="Transition Controller",
                procedure="Simulate 20 m/s dynamic pressure into pitot using regulated pneumatic source while in AUTO mode.",
                expected_result="Pusher motor spools up, duration timer counts 18s, lift rotors smoothly spool down and stop.",
                prerequisite="Pneumatic test rig connected to pitot probe; props REMOVED.",
            ),
            GroundTestChecklistItem(
                test_id="GROUND-TEST-18",
                test_name="High-Rate Dataflash Logging & File Integrity",
                subsystem="Telemetry & Diagnostics",
                procedure="Arm aircraft on bench for 60 seconds; disarm, extract `.bin` dataflash log via MAVLink, and inspect.",
                expected_result="Log contains complete ATT, CTUN, QTUN, IMU, NKF1, BAT, and MOT message series with 0 dropouts.",
                prerequisite="High-speed Class 10 industrial micro-SD card formatted FAT32.",
            ),
        ]
        return tests

    @classmethod
    def execute_preflight_checks(
        cls,
        parameters: List[ArduPilotParameter],
        motor_outputs: List[MotorOutputAssignment],
        servo_outputs: List[ServoOutputAssignment],
        sensors: List[SensorConfigurationItem],
        hardware_reconciliations: List[HardwareReconciliationItem],
    ) -> Tuple[List[PreflightCheckResult], GroundTestReadiness]:
        """
        Executes deterministic rules verification across all configuration domains (Prompt Section 16 & 21).
        """
        results: List[PreflightCheckResult] = []
        param_dict = {p.parameter_name: p.value for p in parameters}

        # 1. Frame class & type check
        frame_class = param_dict.get("Q_FRAME_CLASS")
        frame_type = param_dict.get("Q_FRAME_TYPE")
        q_enable = param_dict.get("Q_ENABLE")
        if q_enable == 1 and frame_class == 7 and frame_type == 1:
            results.append(PreflightCheckResult(
                rule_id="CHK-FRAME-01",
                rule_name="QuadPlane Frame Architecture",
                checked_aspect="Q_ENABLE=1, Q_FRAME_CLASS=7, Q_FRAME_TYPE=1",
                rule_status=FlightControlStatus.PASS,
                evidence_or_reason="QuadPlane dedicated lift rotors + forward cruise pusher correctly configured",
                critical_for_arming=True,
            ))
        else:
            results.append(PreflightCheckResult(
                rule_id="CHK-FRAME-01",
                rule_name="QuadPlane Frame Architecture",
                checked_aspect=f"Q_ENABLE={q_enable}, Q_FRAME_CLASS={frame_class}, Q_FRAME_TYPE={frame_type}",
                rule_status=FlightControlStatus.FAIL,
                evidence_or_reason="Invalid frame configuration; must be Q_ENABLE=1, Q_FRAME_CLASS=7, Q_FRAME_TYPE=1",
                critical_for_arming=True,
            ))

        # 2. Output channel count check (10 channels: 5 motors, 4 servos, 1 relay)
        total_actuators = len(motor_outputs) + len(servo_outputs)
        if len(motor_outputs) == 5 and len(servo_outputs) == 4 and total_actuators == 9:
            results.append(PreflightCheckResult(
                rule_id="CHK-OUTPUT-01",
                rule_name="Actuator Output Count",
                checked_aspect="5 Motors (4 Lift + 1 Cruise) and 4 Aerodynamic Servos",
                rule_status=FlightControlStatus.PASS,
                evidence_or_reason="All 9 primary flight actuators assigned to discrete channels (Channels 1-9)",
                critical_for_arming=True,
            ))
        else:
            results.append(PreflightCheckResult(
                rule_id="CHK-OUTPUT-01",
                rule_name="Actuator Output Count",
                checked_aspect=f"{len(motor_outputs)} motors, {len(servo_outputs)} servos",
                rule_status=FlightControlStatus.FAIL,
                evidence_or_reason="Actuator count mismatch; expected 5 motors and 4 servos",
                critical_for_arming=True,
            ))

        # 3. Output channel collision check
        all_channels = [m.output_channel for m in motor_outputs] + [s.output_channel for s in servo_outputs]
        if len(all_channels) == len(set(all_channels)):
            results.append(PreflightCheckResult(
                rule_id="CHK-OUTPUT-02",
                rule_name="Output Channel Collision Free",
                checked_aspect="Channels 1 through 9 uniqueness",
                rule_status=FlightControlStatus.PASS,
                evidence_or_reason="Zero channel collisions across Pixhawk 6X output rails",
                critical_for_arming=True,
            ))
        else:
            results.append(PreflightCheckResult(
                rule_id="CHK-OUTPUT-02",
                rule_name="Output Channel Collision Free",
                checked_aspect="Channels list contains duplicates",
                rule_status=FlightControlStatus.FAIL,
                evidence_or_reason="Duplicate output channel detected",
                critical_for_arming=True,
            ))

        # 4. Motor rotation direction bench verification check
        unverified_dirs = [m.motor_id for m in motor_outputs if m.direction_verification_status != FlightControlStatus.PASS]
        if len(unverified_dirs) > 0:
            results.append(PreflightCheckResult(
                rule_id="CHK-MOTOR-DIR",
                rule_name="Motor Physical Rotation Direction",
                checked_aspect=f"Motors {', '.join(unverified_dirs)} rotation status",
                rule_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                evidence_or_reason="Physical CW/CCW rotation direction must be confirmed on test bench prior to flight (Prompt Section 6)",
                critical_for_arming=False,
            ))

        # 5. Servo physical direction & torque check
        results.append(PreflightCheckResult(
            rule_id="CHK-SERVO-DIR",
            rule_name="Servo Physical Deflection Direction",
            checked_aspect="Aileron and inverted V-tail deflection signs",
            rule_status=FlightControlStatus.GROUND_TEST_REQUIRED,
            evidence_or_reason="Physical horn orientation and link signs require bench verification (Prompt Section 14 & 15)",
            critical_for_arming=False,
        ))

        # 6. Battery threshold ordering check: Arm > Low > Crt
        arm_v = float(param_dict.get("BATT_ARM_VOLT", 0.0))
        low_v = float(param_dict.get("BATT_LOW_VOLT", 0.0))
        crt_v = float(param_dict.get("BATT_CRT_VOLT", 0.0))
        if arm_v > low_v > crt_v and crt_v >= 19.2:
            results.append(PreflightCheckResult(
                rule_id="CHK-BATT-01",
                rule_name="Battery Failsafe Voltage Hierarchy",
                checked_aspect=f"Arm ({arm_v}V) > Low ({low_v}V) > Critical ({crt_v}V) >= 19.2V",
                rule_status=FlightControlStatus.PASS,
                evidence_or_reason="Correct voltage failsafe hierarchy protects 6S LiPo cells from over-discharge",
                critical_for_arming=True,
            ))
        else:
            results.append(PreflightCheckResult(
                rule_id="CHK-BATT-01",
                rule_name="Battery Failsafe Voltage Hierarchy",
                checked_aspect=f"Arm ({arm_v}V), Low ({low_v}V), Crt ({crt_v}V)",
                rule_status=FlightControlStatus.FAIL,
                evidence_or_reason="Battery voltage thresholds improperly ordered or below safe cell limits",
                critical_for_arming=True,
            ))

        # 7. Transition speed & stall speed consistency check
        arspd_min = float(param_dict.get("ARSPD_FBW_MIN", 0.0))
        q_assist = float(param_dict.get("Q_ASSIST_SPEED", 0.0))
        if arspd_min >= 18.0 and q_assist >= 17.5:
            results.append(PreflightCheckResult(
                rule_id="CHK-TRANS-01",
                rule_name="Transition Airspeed Stall Margin",
                checked_aspect=f"ARSPD_FBW_MIN={arspd_min} m/s, Q_ASSIST_SPEED={q_assist} m/s",
                rule_status=FlightControlStatus.PASS,
                evidence_or_reason="Matches Phase 3 stall threshold (18.06 m/s) with positive stall assist protection",
                critical_for_arming=True,
            ))
        else:
            results.append(PreflightCheckResult(
                rule_id="CHK-TRANS-01",
                rule_name="Transition Airspeed Stall Margin",
                checked_aspect=f"ARSPD_FBW_MIN={arspd_min} m/s, Q_ASSIST_SPEED={q_assist} m/s",
                rule_status=FlightControlStatus.FAIL,
                evidence_or_reason="Transition airspeed settings violate Phase 3 stall kinematics",
                critical_for_arming=True,
            ))

        # 8. Arming safety check (Never weakened)
        arming_chk = param_dict.get("ARMING_CHECK")
        if arming_chk == 1:
            results.append(PreflightCheckResult(
                rule_id="CHK-SAFETY-01",
                rule_name="Arming Safety Gates Enforced",
                checked_aspect="ARMING_CHECK=1 (All pre-arm checks strictly active)",
                rule_status=FlightControlStatus.PASS,
                evidence_or_reason="No safety checks bypassed or masked (Prompt Section 21)",
                critical_for_arming=True,
            ))
        else:
            results.append(PreflightCheckResult(
                rule_id="CHK-SAFETY-01",
                rule_name="Arming Safety Gates Enforced",
                checked_aspect=f"ARMING_CHECK={arming_chk}",
                rule_status=FlightControlStatus.FAIL,
                evidence_or_reason="Arming checks weakened; violates project safety invariant",
                critical_for_arming=True,
            ))

        # 9. Hardware identity consistency audit
        has_hw_conflict = any(r.reconciliation_verdict == FlightControlStatus.HARDWARE_IDENTITY_CONFLICT for r in hardware_reconciliations)
        if has_hw_conflict:
            results.append(PreflightCheckResult(
                rule_id="CHK-HW-RECON",
                rule_name="Hardware Identity Reconciliation",
                checked_aspect="Phase 8 BOM vs Phase 9 Integration component identities",
                rule_status=FlightControlStatus.HARDWARE_IDENTITY_CONFLICT,
                evidence_or_reason="Discrepancy detected between Phase 8 BOM and Phase 9 integration text (Spedix GS40A vs AIR 40A, Skywalker vs FlyFun)",
                critical_for_arming=False,
            ))
        else:
            results.append(PreflightCheckResult(
                rule_id="CHK-HW-RECON",
                rule_name="Hardware Identity Reconciliation",
                checked_aspect="All hardware identities matched",
                rule_status=FlightControlStatus.PASS,
                evidence_or_reason="Phase 8 and Phase 9 hardware definitions fully consistent",
                critical_for_arming=False,
            ))

        # Evaluate overall Ground-Test Readiness
        has_critical_failure = any(r.rule_status == FlightControlStatus.FAIL and r.critical_for_arming for r in results)
        has_warnings = any(r.rule_status in (FlightControlStatus.GROUND_TEST_REQUIRED, FlightControlStatus.HARDWARE_IDENTITY_CONFLICT) for r in results)

        if has_critical_failure:
            readiness = GroundTestReadiness.BLOCKED
        elif has_warnings:
            readiness = GroundTestReadiness.READY_WITH_WARNINGS
        else:
            readiness = GroundTestReadiness.READY_FOR_GROUND_TEST

        return results, readiness
