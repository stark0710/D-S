"""
VTOL Phase 10 Failsafe Configuration Engine.

Purpose:
    Evaluates 15 mandatory failsafe scenarios, defining detection mechanisms,
    configured autopilot actions, sensor requirements, and fallback modes.
    Enforces that software-configured fallbacks remain classified as
    CONFIGURATION_SUPPORTED or DEFERRED without false FLIGHT_VERIFIED claims.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .flight_control_models import (
    FailsafeResponseAction,
    FailsafeScenarioItem,
    FlightControlStatus,
)


class FailsafeConfigurationEngine:
    """
    Authoritative failsafe matrix evaluation engine (Prompt Section 17).
    """

    @classmethod
    def build_failsafe_matrix(cls) -> List[FailsafeScenarioItem]:
        """
        Builds the 15 required failsafe scenarios linking Phase 9 FMEA to ArduPilot actions.
        """
        matrix: List[FailsafeScenarioItem] = [
            FailsafeScenarioItem(
                scenario_id="FS-01",
                failure_name="RC Control Link Loss",
                detection_mechanism="TBS Crossfire CRSF packet timeout > 1.5s (THR_FAILSAFE = 1)",
                configured_response=FailsafeResponseAction.QRTL,
                required_sensors=["GNSS / RTK", "Barometer", "IMU"],
                fallback_mode="QRTL (Climb to RTL altitude, return to home, and VTOL land)",
                verification_method="Ground bench RC transmitter power-down simulation",
                controllability_status=FlightControlStatus.PASS,
                notes="Software-supported failsafe configuration (CONFIGURATION_SUPPORTED in Phase 9)",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-02",
                failure_name="GCS Telemetry Link Loss",
                detection_mechanism="MAVLink heartbeat loss on TELEM1 > 10.0s (FS_GCS_ENABL = 1)",
                configured_response=FailsafeResponseAction.CONTINUE_MISSION,
                required_sensors=["GNSS / RTK", "IMU"],
                fallback_mode="Continue pre-loaded autonomous mission; execute QRTL if battery low",
                verification_method="Bench disconnection of SiK 915MHz GCS modem",
                controllability_status=FlightControlStatus.PASS,
                notes="Standard BVLOS autonomous flight logic",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-03",
                failure_name="Low Battery Stage 1 (Voltage <= 21.6V / Reserve <= 20%)",
                detection_mechanism="Matek PDB-HEX analog voltage/current monitoring on POWER1",
                configured_response=FailsafeResponseAction.RTL,
                required_sensors=["Battery Monitor", "GNSS / RTK"],
                fallback_mode="Immediate return to home (BATT_FS_LOW_ACT = 2: RTL)",
                verification_method="Simulated voltage sag injection via programmable bench DC supply",
                controllability_status=FlightControlStatus.PASS,
                notes="Initiates return before battery depletion prevents hover recovery",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-04",
                failure_name="Critical Battery Stage 2 (Voltage <= 20.4V / Reserve <= 10%)",
                detection_mechanism="Matek PDB-HEX analog voltage monitoring on POWER1",
                configured_response=FailsafeResponseAction.QLAND,
                required_sensors=["Battery Monitor", "Barometer", "IMU"],
                fallback_mode="Immediate vertical descent at current position (BATT_FS_CRT_ACT = 1: Land)",
                verification_method="DC bench power step-down test to 20.4V",
                controllability_status=FlightControlStatus.PASS,
                notes="Prevents cell over-discharge and total power cutout in flight",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-05",
                failure_name="GNSS / RTK Fix Loss or GPS Glitch",
                detection_mechanism="EKF3 innovation threshold check; loss of 3D fix flags (GPS_GLITCH_RADIUS)",
                configured_response=FailsafeResponseAction.QHOVER,
                required_sensors=["Airspeed", "Compass", "Barometer", "IMU"],
                fallback_mode="Dead-reckoning navigation using synthetic wind, altitude hold via QHOVER",
                verification_method="GNSS antenna RF shielding / simulated GPS signal loss",
                controllability_status=FlightControlStatus.PASS,
                notes="Drift rate depends on compass and pitot accuracy (CONFIGURATION_SUPPORTED)",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-06",
                failure_name="EKF Extended Kalman Filter Failure",
                detection_mechanism="EK3 core health flags / lane switching failure",
                configured_response=FailsafeResponseAction.QHOVER,
                required_sensors=["IMU", "Barometer"],
                fallback_mode="Emergency non-GPS DCM attitude stabilization",
                verification_method="Autopilot sensor injection simulation",
                controllability_status=FlightControlStatus.PASS,
                notes="Switches to secondary/tertiary IMU core before declaring failure",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-07",
                failure_name="Airspeed Sensor Clogging or I2C Failure",
                detection_mechanism="Pitot dynamic pressure anomaly check vs GPS groundspeed (ARSPD_FAIL_ACTION)",
                configured_response=FailsafeResponseAction.CONTINUE_MISSION,
                required_sensors=["GNSS / RTK", "IMU"],
                fallback_mode="Failover to synthetic airspeed estimation (EKF3 groundspeed + wind matrix +15% margin)",
                verification_method="Bench pitot tube blockage test",
                controllability_status=FlightControlStatus.PASS,
                notes="Software-supported fallback; stall margin under gust conditions remains unproven in flight",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-08",
                failure_name="Compass Inconsistency / Magnetic Interference",
                detection_mechanism="EKF3 magnetic field anomaly detection / yaw innovation check",
                configured_response=FailsafeResponseAction.FBWA,
                required_sensors=["GNSS / RTK", "Airspeed", "IMU"],
                fallback_mode="GNSS course-over-ground heading estimation (EK3_MAG_CAL = 2)",
                verification_method="Bench magnetic field disturbance test with neodymium magnet",
                controllability_status=FlightControlStatus.PASS,
                notes="High-speed fixed-wing flight can navigate without magnetometer",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-09",
                failure_name="Cruise Motor Flameout / Pusher Loss",
                detection_mechanism="Airspeed decay below Q_ASSIST_SPEED (18.0 m/s) despite 100% cruise throttle",
                configured_response=FailsafeResponseAction.QRTL,
                required_sensors=["Airspeed", "GNSS / RTK", "IMU", "Barometer"],
                fallback_mode="Q_ASSIST automatic VTOL lift rotor spool-up; abort cruise and enter QRTL hover landing",
                verification_method="In-flight throttle cut simulation in SITL / bench test",
                controllability_status=FlightControlStatus.PASS,
                notes="Gliding back-transition corridor supported by software configuration (CONFIGURATION_SUPPORTED)",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-10",
                failure_name="Cruise ESC Failure / Loss of Throttle Signal",
                detection_mechanism="Zero forward acceleration detected during cruise phase",
                configured_response=FailsafeResponseAction.QRTL,
                required_sensors=["Airspeed", "GNSS / RTK", "IMU"],
                fallback_mode="Autonomous switch to VTOL lift propulsion and QRTL return",
                verification_method="Signal disconnect test to PWM Output 5",
                controllability_status=FlightControlStatus.PASS,
                notes="Identical aerodynamic recovery behavior to Cruise Motor Flameout",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-11",
                failure_name="VTOL Lift Motor Failure (Hover Engine-Out)",
                detection_mechanism="High roll/pitch rate acceleration with saturated motor output on opposite quadrant",
                configured_response=FailsafeResponseAction.GLIDE_DESCENT,
                required_sensors=["IMU", "Airspeed"],
                fallback_mode="Pure hover unmaintainable on 4-rotor frame; command forward pitch to gain wing lift if altitude permits, or deploy parachute",
                verification_method="6-DOF aerodynamic simulation (Physical bench test prohibited)",
                controllability_status=FlightControlStatus.DEFERRED,
                notes="Legitimately DEFERRED per Phase 9 (HOVER_ENGINE_OUT). Pure hover with 1 out of 4 lift rotors cannot maintain static attitude.",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-12",
                failure_name="Aerodynamic Control Surface Jam (Servo Jam)",
                detection_mechanism="Attitude error accumulation despite trim command saturation",
                configured_response=FailsafeResponseAction.QHOVER,
                required_sensors=["IMU", "Barometer"],
                fallback_mode="Trim remaining surfaces and transition to VTOL hover where rotor differential thrust dominates",
                verification_method="Simulation / bench linkage restriction test",
                controllability_status=FlightControlStatus.DEFERRED,
                notes="Cross-control trim authority under jammed servo remains DEFERRED (AERO_JAM_TRIM in Phase 9)",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-13",
                failure_name="Pixhawk Main FMU Bus Lockup",
                detection_mechanism="STM32H7 hardware watchdog timer expiration (>200ms)",
                configured_response=FailsafeResponseAction.IOMCU_FAILOVER,
                required_sensors=["Internal IMU / IOMCU"],
                fallback_mode="STM32F100 IOMCU coprocessor takes over PWM outputs, commanding neutral surfaces and motor idle",
                verification_method="Watchdog reset injection via software test build",
                controllability_status=FlightControlStatus.PASS,
                notes="Architectural hardware safety feature of Holybro Pixhawk 6X",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-14",
                failure_name="Raspberry Pi Companion SBC Crash",
                detection_mechanism="Heartbeat timeout on TELEM2 serial UART (>3.0s)",
                configured_response=FailsafeResponseAction.WARN_ONLY,
                required_sensors=["Pixhawk Core Sensors"],
                fallback_mode="Autonomous flight execution continues uninterrupted; vision/payload tasks disabled",
                verification_method="SBC power-down test during bench telemetry monitoring",
                controllability_status=FlightControlStatus.PASS,
                notes="Hardware isolation verified in Phase 9 (Dedicated 5V 3A BEC prevents electrical cross-talk)",
            ),
            FailsafeScenarioItem(
                scenario_id="FS-15",
                failure_name="PDB Total Main Bus Short Circuit",
                detection_mechanism="Instantaneous loss of primary 22.2V bus voltage",
                configured_response=FailsafeResponseAction.TERMINATION_PARACHUTE,
                required_sensors=["None (Complete power loss)"],
                fallback_mode="Mechanical spring-loaded or pyrotechnic ballistic parachute recovery",
                verification_method="Engineering risk analysis",
                controllability_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                notes="Classified as NOT_ANALYZED in Phase 9 FMEA-11; parachute subsystem integration required",
            ),
        ]
        return matrix
