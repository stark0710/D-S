"""
VTOL Phase 10 ArduPilot QuadPlane Configuration Engine.

Purpose:
    Generates the complete, deterministic, machine-readable parameter suite for
    Holybro Pixhawk 6X running ArduPilot QuadPlane (Plane 4.4+).
    Ensures every parameter has strict provenance, justification, and confidence ratings.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .flight_control_models import (
    ArduPilotParameter,
    FlightControlStatus,
    ParameterConfidence,
    ParameterSourceType,
)
from .parameter_provenance import ParameterProvenanceRegistry
from .transition_configuration import TransitionConfigurationEngine


class ArduPilotConfigurationEngine:
    """
    Authoritative generator for complete ArduPilot QuadPlane parameter configuration.
    """

    @classmethod
    def generate_all_parameters(
        cls,
        vtol_esc_protocol: str = "DSHOT600",
    ) -> List[ArduPilotParameter]:
        """
        Synthesizes the complete parameter suite across all subsystem groups.
        """
        params: List[ArduPilotParameter] = []

        # =========================================================================
        # 1. QUADPLANE FRAME & ARCHITECTURE PARAMETERS
        # =========================================================================
        params.append(ArduPilotParameter(
            parameter_name="Q_ENABLE",
            value=1,
            unit="boolean",
            purpose="Enables QuadPlane hybrid VTOL flight modes and motor controllers",
            source="Phase 1 QuadPlane Architecture",
            source_type=ParameterSourceType.PHASE_1_OUTPUT,
            required_or_optional="REQUIRED",
            confidence=ParameterConfidence.HIGH,
            status=FlightControlStatus.PASS,
            notes="Activates ArduPilot Plane QuadPlane subsystem",
        ))
        params.append(ArduPilotParameter(
            parameter_name="Q_FRAME_CLASS",
            value=7,
            unit="enum",
            purpose="QuadPlane frame class (7 = QuadPlane: dedicated lift rotors + forward pusher)",
            source="Phase 1 Aircraft Requirements",
            source_type=ParameterSourceType.PHASE_1_OUTPUT,
            required_or_optional="REQUIRED",
            confidence=ParameterConfidence.HIGH,
            status=FlightControlStatus.PASS,
            notes="Separates lift motors from forward cruise pusher motor",
        ))
        params.append(ArduPilotParameter(
            parameter_name="Q_FRAME_TYPE",
            value=1,
            unit="enum",
            purpose="QuadPlane motor geometry layout (1 = Quad-X frame)",
            source="Phase 1 Motor Boom Geometry",
            source_type=ParameterSourceType.PHASE_1_OUTPUT,
            required_or_optional="REQUIRED",
            confidence=ParameterConfidence.HIGH,
            status=FlightControlStatus.PASS,
            notes="4 lift rotors positioned on dual outboard wing booms in standard X arrangement",
        ))

        # =========================================================================
        # 2. ACTUATOR & SERVO OUTPUT FUNCTIONS (CHANNELS 1 - 10)
        # =========================================================================
        params.extend([
            ArduPilotParameter(
                parameter_name="SERVO1_FUNCTION",
                value=33,
                unit="enum",
                purpose="Output 1 function assignment: Motor 1 (Front-Left Lift Motor)",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO2_FUNCTION",
                value=34,
                unit="enum",
                purpose="Output 2 function assignment: Motor 2 (Front-Right Lift Motor)",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO3_FUNCTION",
                value=35,
                unit="enum",
                purpose="Output 3 function assignment: Motor 3 (Rear-Left Lift Motor)",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO4_FUNCTION",
                value=36,
                unit="enum",
                purpose="Output 4 function assignment: Motor 4 (Rear-Right Lift Motor)",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO5_FUNCTION",
                value=70,
                unit="enum",
                purpose="Output 5 function assignment: Throttle (Cruise Pusher Motor)",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO6_FUNCTION",
                value=4,
                unit="enum",
                purpose="Output 6 function assignment: Left Outboard Aileron",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO7_FUNCTION",
                value=4,
                unit="enum",
                purpose="Output 7 function assignment: Right Outboard Aileron",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO8_FUNCTION",
                value=77,
                unit="enum",
                purpose="Output 8 function assignment: V-Tail Left Ruddervator Surface",
                source="Phase 9 I/O Pinout Allocation & Inverted V-Tail Mixer",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO9_FUNCTION",
                value=78,
                unit="enum",
                purpose="Output 9 function assignment: V-Tail Right Ruddervator Surface",
                source="Phase 9 I/O Pinout Allocation & Inverted V-Tail Mixer",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="SERVO10_FUNCTION",
                value=28,
                unit="enum",
                purpose="Output 10 function assignment: Camera Shutter Trigger Relay (Sony RX0 II)",
                source="Phase 9 I/O Pinout Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
        ])

        # =========================================================================
        # 3. ESC PROTOCOL & DSHOT CONFIGURATION
        # =========================================================================
        if vtol_esc_protocol == "DSHOT600":
            params.append(ArduPilotParameter(
                parameter_name="MOT_PWM_TYPE",
                value=6,
                unit="enum",
                purpose="Output protocol for lift motor ESC channels (6 = DShot600)",
                source="Phase 8 Spedix GS40A ESC Datasheet Specification",
                source_type=ParameterSourceType.HARDWARE_DATASHEET,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Requires Spedix GS40A ESC; provides sub-millisecond digital throttle commands",
            ))
            params.append(ArduPilotParameter(
                parameter_name="SERVO_BLH_AUTO",
                value=1,
                unit="boolean",
                purpose="Enables automatic BLHeli/DShot telemetry pass-through on motor channels 1-4",
                source="Official ArduPilot Documentation",
                source_type=ParameterSourceType.ARDUPILOT_DOCUMENTATION,
                confidence=ParameterConfidence.HIGH,
            ))
        else:
            params.append(ArduPilotParameter(
                parameter_name="MOT_PWM_TYPE",
                value=0,
                unit="enum",
                purpose="Output protocol for lift motor ESC channels (0 = Normal PWM / Fast PWM)",
                source="Fallback / Alternative ESC Specification",
                source_type=ParameterSourceType.CONFIGURABLE_ASSUMPTION,
                confidence=ParameterConfidence.MEDIUM,
                status=FlightControlStatus.PASS,
                notes="Used if analog/Fast PWM ESC (e.g., T-Motor AIR 40A) is selected",
            ))

        # =========================================================================
        # 4. TRANSITION KINEMATICS & AIRSPEED LIMITS (FROM PHASE 3 & 6)
        # =========================================================================
        params.extend(TransitionConfigurationEngine.get_transition_parameters())

        # =========================================================================
        # 5. BATTERY & POWER MONITORING (FROM PHASE 4 & 8)
        # =========================================================================
        params.extend([
            ArduPilotParameter(
                parameter_name="BATT_MONITOR",
                value=4,
                unit="enum",
                purpose="Battery monitor sensor type (4 = Analog Voltage and Current via PDB)",
                source="Phase 8 Matek PDB-HEX Hardware Specification",
                source_type=ParameterSourceType.PHASE_8_HARDWARE,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_CAPACITY",
                value=22000,
                unit="mAh",
                purpose="Total usable nominal battery capacity",
                source="Phase 8 Tattu Plus 22000mAh 6S Battery Pack (`BOM-008`)",
                source_type=ParameterSourceType.PHASE_8_HARDWARE,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_ARM_VOLT",
                value=24.6,
                unit="V",
                purpose="Pre-arm voltage check minimum threshold (4.10V / cell)",
                source="Phase 4 Energy Calculations (Full charge is 25.2V)",
                source_type=ParameterSourceType.PHASE_4_OUTPUT,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_LOW_VOLT",
                value=21.6,
                unit="V",
                purpose="Stage 1 low-voltage failsafe warning threshold (3.60V / cell under load)",
                source="Phase 4 Battery Discharge Curve Analysis",
                source_type=ParameterSourceType.PHASE_4_OUTPUT,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_CRT_VOLT",
                value=20.4,
                unit="V",
                purpose="Stage 2 critical-voltage failsafe landing threshold (3.40V / cell under load)",
                source="Phase 4 LiPo Safe Cutoff Limit",
                source_type=ParameterSourceType.PHASE_4_OUTPUT,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_LOW_MAH",
                value=4400,
                unit="mAh",
                purpose="Low battery capacity remaining threshold (20% reserve remaining)",
                source="Phase 4 Energy Reserve Margin Requirement (20% SOC)",
                source_type=ParameterSourceType.PROJECT_REQUIREMENT,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_CRT_MAH",
                value=2200,
                unit="mAh",
                purpose="Critical battery capacity remaining threshold (10% emergency reserve)",
                source="Phase 4 Emergency Hover Landing Allowance",
                source_type=ParameterSourceType.PROJECT_REQUIREMENT,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_FS_LOW_ACT",
                value=2,
                unit="enum",
                purpose="Action when Stage 1 low battery threshold is reached (2 = RTL)",
                source="Phase 9 FMEA Failsafe Strategy (FMEA-10)",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="BATT_FS_CRT_ACT",
                value=1,
                unit="enum",
                purpose="Action when Stage 2 critical battery threshold is reached (1 = Land / QLAND)",
                source="Phase 9 FMEA Failsafe Strategy (FMEA-10)",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
        ])

        # =========================================================================
        # 6. NAVIGATION, SENSORS & EKF3
        # =========================================================================
        params.extend([
            ArduPilotParameter(
                parameter_name="ARSPD_TYPE",
                value=1,
                unit="enum",
                purpose="Airspeed sensor driver type (1 = MS4525 / Matek ASPD-4525 on I2C)",
                source="Phase 8 Matek ASPD-4525 Airspeed Sensor Specification",
                source_type=ParameterSourceType.PHASE_8_HARDWARE,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="ARSPD_USE",
                value=1,
                unit="boolean",
                purpose="Enables airspeed sensor dynamic pressure in flight control and EKF3",
                source="Official ArduPilot Documentation",
                source_type=ParameterSourceType.ARDUPILOT_DOCUMENTATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="GPS_TYPE",
                value=2,
                unit="enum",
                purpose="Primary GPS driver type (2 = u-blox binary protocol for Holybro F9P RTK)",
                source="Phase 8 Holybro H-RTK F9P Datasheet",
                source_type=ParameterSourceType.PHASE_8_HARDWARE,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="EK3_ENABLE",
                value=1,
                unit="boolean",
                purpose="Enables Extended Kalman Filter 3 (EKF3) high-fidelity navigation core",
                source="Official ArduPilot Documentation",
                source_type=ParameterSourceType.ARDUPILOT_DOCUMENTATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="COMPASS_TYPEMASK",
                value=0,
                unit="bitmask",
                purpose="Magnetometer driver mask (0 = All drivers enabled, primary external F9P)",
                source="Phase 9 I/O Allocation",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
        ])

        # =========================================================================
        # 7. FAILSAFE & RECOVERY MODES
        # =========================================================================
        params.extend([
            ArduPilotParameter(
                parameter_name="THR_FAILSAFE",
                value=1,
                unit="enum",
                purpose="RC loss failsafe action (1 = Enabled, triggers RTL / QRTL on packet loss)",
                source="Phase 9 FMEA-07 Specification",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="FS_GCS_ENABL",
                value=1,
                unit="enum",
                purpose="GCS telemetry loss failsafe (1 = Heartbeat timeout enabled)",
                source="Phase 9 FMEA-08 Specification",
                source_type=ParameterSourceType.PHASE_9_INTEGRATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="Q_RTL_MODE",
                value=1,
                unit="enum",
                purpose="RTL return mode for QuadPlane (1 = Return via fixed-wing, then VTOL land)",
                source="Phase 1 QuadPlane Mission Architecture",
                source_type=ParameterSourceType.PHASE_1_OUTPUT,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="RTL_ALT",
                value=5000,
                unit="cm",
                purpose="RTL cruise altitude (50.0m AGL safe obstacle clearance)",
                source="Phase 1 Mission Profile",
                source_type=ParameterSourceType.PHASE_1_OUTPUT,
                confidence=ParameterConfidence.HIGH,
            ),
        ])

        # =========================================================================
        # 8. PRE-ARM SAFETY GATES & LOGGING
        # =========================================================================
        params.extend([
            ArduPilotParameter(
                parameter_name="ARMING_CHECK",
                value=1,
                unit="bitmask",
                purpose="Pre-arm safety check mask (1 = All hardware, EKF, sensor, and battery checks enabled)",
                source="Prompt Section 21: Never bypass or weaken safety checks",
                source_type=ParameterSourceType.PROJECT_REQUIREMENT,
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Strictly enforces pre-arm validation; safety checks are never weakened",
            ),
            ArduPilotParameter(
                parameter_name="LOG_BITMASK",
                value=65535,
                unit="bitmask",
                purpose="Dataflash logging coverage (Attitude, Motors, EKF, Navigation, Batteries, Failsafes)",
                source="Prompt Section 20 Logging Requirements",
                source_type=ParameterSourceType.ARDUPILOT_DOCUMENTATION,
                confidence=ParameterConfidence.HIGH,
            ),
            ArduPilotParameter(
                parameter_name="LOG_DISARMED",
                value=1,
                unit="boolean",
                purpose="Enables logging while disarmed to capture pre-flight sensor initialization",
                source="Official ArduPilot Documentation",
                source_type=ParameterSourceType.ARDUPILOT_DOCUMENTATION,
                confidence=ParameterConfidence.HIGH,
            ),
        ])

        return params
