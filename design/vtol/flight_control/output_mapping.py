"""
VTOL Phase 10 Output and Actuator Mapping Engine.

Purpose:
    Maps the 10 discrete Pixhawk 6X actuator and relay channels to propulsion motors,
    aerodynamic control surfaces, and payload triggers.
    Enforces strict protocol matching (DShot600 vs PWM) and explicit unverified
    rotation direction markers pending physical motor bench testing.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .flight_control_models import (
    FlightControlStatus,
    MotorOutputAssignment,
    MotorRotationDirection,
    OutputProtocol,
    ServoOutputAssignment,
)


class OutputMappingEngine:
    """
    Authoritative generator and validator for Pixhawk 6X actuator output channels.
    """

    @classmethod
    def build_motor_output_mappings(
        cls,
        vtol_esc_model: str = "Spedix GS40A 6S",
        cruise_esc_model: str = "Hobbywing Skywalker 40A V2",
    ) -> List[MotorOutputAssignment]:
        """
        Builds output mapping for the 4 VTOL lift motors and 1 cruise pusher motor.
        Strictly marks physical rotation direction as UNVERIFIED_REQUIRES_BENCH_TEST per Section 6.
        """
        # Determine protocol based on ESC model
        if "Spedix" in vtol_esc_model:
            vtol_protocol = OutputProtocol.DSHOT600
            freq_hz = None  # DShot is digital serial bitstream, not PWM frequency
        elif "AIR 40A" in vtol_esc_model:
            vtol_protocol = OutputProtocol.FAST_PWM_400HZ
            freq_hz = 400.0
        else:
            vtol_protocol = OutputProtocol.CONFIGURATION_PENDING
            freq_hz = None

        cruise_protocol = OutputProtocol.STANDARD_PWM_50HZ
        cruise_freq_hz = 50.0  # Safe standard fixed-wing ESC analog PWM rate

        motors: List[MotorOutputAssignment] = [
            MotorOutputAssignment(
                motor_id="M1",
                physical_position="Front-Left VTOL Boom Station (x=0.25m, y=-0.60m, z=+0.04m)",
                output_channel=1,
                assigned_role="VTOL_MOTOR_1",
                hardware_esc=vtol_esc_model,
                hardware_motor="T-Motor MN4014 KV330",
                hardware_propeller="T-Motor P16x5.4 Carbon Fiber",
                protocol=vtol_protocol,
                signal_frequency_hz=freq_hz,
                nominal_rotation_direction=MotorRotationDirection.CW,  # Nominal ArduPilot Quad-X convention
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                failsafe_action="Immediate DShot Disarm / Zero Throttle command",
                notes="Physical rotation direction must be confirmed on bench test (Prompt Section 6 constraint: UNVERIFIED — REQUIRES BENCH TEST).",
            ),
            MotorOutputAssignment(
                motor_id="M2",
                physical_position="Front-Right VTOL Boom Station (x=0.25m, y=+0.60m, z=+0.04m)",
                output_channel=2,
                assigned_role="VTOL_MOTOR_2",
                hardware_esc=vtol_esc_model,
                hardware_motor="T-Motor MN4014 KV330",
                hardware_propeller="T-Motor P16x5.4 Carbon Fiber",
                protocol=vtol_protocol,
                signal_frequency_hz=freq_hz,
                nominal_rotation_direction=MotorRotationDirection.CCW,
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                failsafe_action="Immediate DShot Disarm / Zero Throttle command",
                notes="Physical rotation direction must be confirmed on bench test (Prompt Section 6 constraint: UNVERIFIED — REQUIRES BENCH TEST).",
            ),
            MotorOutputAssignment(
                motor_id="M3",
                physical_position="Rear-Left VTOL Boom Station (x=0.75m, y=-0.60m, z=+0.04m)",
                output_channel=3,
                assigned_role="VTOL_MOTOR_3",
                hardware_esc=vtol_esc_model,
                hardware_motor="T-Motor MN4014 KV330",
                hardware_propeller="T-Motor P16x5.4 Carbon Fiber",
                protocol=vtol_protocol,
                signal_frequency_hz=freq_hz,
                nominal_rotation_direction=MotorRotationDirection.CCW,
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                failsafe_action="Immediate DShot Disarm / Zero Throttle command",
                notes="Physical rotation direction must be confirmed on bench test (Prompt Section 6 constraint: UNVERIFIED — REQUIRES BENCH TEST).",
            ),
            MotorOutputAssignment(
                motor_id="M4",
                physical_position="Rear-Right VTOL Boom Station (x=0.75m, y=+0.60m, z=+0.04m)",
                output_channel=4,
                assigned_role="VTOL_MOTOR_4",
                hardware_esc=vtol_esc_model,
                hardware_motor="T-Motor MN4014 KV330",
                hardware_propeller="T-Motor P16x5.4 Carbon Fiber",
                protocol=vtol_protocol,
                signal_frequency_hz=freq_hz,
                nominal_rotation_direction=MotorRotationDirection.CW,
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                failsafe_action="Immediate DShot Disarm / Zero Throttle command",
                notes="Physical rotation direction must be confirmed on bench test (Prompt Section 6 constraint: UNVERIFIED — REQUIRES BENCH TEST).",
            ),
            MotorOutputAssignment(
                motor_id="M5",
                physical_position="Fuselage Tail Firewall Pusher (x=0.92m, y=0.00m, z=+0.01m)",
                output_channel=5,
                assigned_role="CRUISE_MOTOR",
                hardware_esc=cruise_esc_model,
                hardware_motor="T-Motor AT2820 KV880",
                hardware_propeller="APC 11x7 Thin Electric Pusher",
                protocol=cruise_protocol,
                signal_frequency_hz=cruise_freq_hz,
                nominal_rotation_direction=MotorRotationDirection.CW,  # Standard pusher facing aft
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                failsafe_action="Zero throttle PWM pulse (1000us) on signal loss / disarm",
                notes="Pusher motor rotation must push air rearward; requires physical propeller and motor spin bench test.",
            ),
        ]
        return motors

    @classmethod
    def build_servo_output_mappings(
        cls,
        servo_model: str = "KST DS215MG V8.0",
    ) -> List[ServoOutputAssignment]:
        """
        Builds output mapping for the 4 aerodynamic control surface servos (Channels 6-9).
        """
        servos: List[ServoOutputAssignment] = [
            ServoOutputAssignment(
                surface_name="Left Outboard Aileron",
                output_channel=6,
                servo_function_param="SERVO6_FUNCTION",
                servo_function_id=4,  # ArduPilot Function 4: Aileron
                hardware_servo=servo_model,
                pwm_min_us=1000,
                pwm_neutral_us=1500,
                pwm_max_us=2000,
                pwm_trim_us=1500,
                protocol=OutputProtocol.DIGITAL_PWM_333HZ,
                signal_frequency_hz=333.0,
                direction_reversed=False,
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                hinge_torque_status=FlightControlStatus.DEFERRED,
                notes="Left wing outboard roll control surface. Physical deflection direction must be verified on bench test.",
            ),
            ServoOutputAssignment(
                surface_name="Right Outboard Aileron",
                output_channel=7,
                servo_function_param="SERVO7_FUNCTION",
                servo_function_id=4,  # ArduPilot Function 4: Aileron (or dual aileron via trim/reverse)
                hardware_servo=servo_model,
                pwm_min_us=1000,
                pwm_neutral_us=1500,
                pwm_max_us=2000,
                pwm_trim_us=1500,
                protocol=OutputProtocol.DIGITAL_PWM_333HZ,
                signal_frequency_hz=333.0,
                direction_reversed=False,
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                hinge_torque_status=FlightControlStatus.DEFERRED,
                notes="Right wing outboard roll control surface. Direction relative to left aileron requires bench verification.",
            ),
            ServoOutputAssignment(
                surface_name="Left Ruddervator (Inverted V-Tail)",
                output_channel=8,
                servo_function_param="SERVO8_FUNCTION",
                servo_function_id=77,  # ArduPilot Function 77: V-Tail Left (Pitch + Yaw mixing)
                hardware_servo=servo_model,
                pwm_min_us=1000,
                pwm_neutral_us=1500,
                pwm_max_us=2000,
                pwm_trim_us=1500,
                protocol=OutputProtocol.DIGITAL_PWM_333HZ,
                signal_frequency_hz=333.0,
                direction_reversed=False,
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                hinge_torque_status=FlightControlStatus.DEFERRED,
                notes="Port empennage control surface. Inverted V-tail geometry requires sign check for pitch up/down and yaw left/right.",
            ),
            ServoOutputAssignment(
                surface_name="Right Ruddervator (Inverted V-Tail)",
                output_channel=9,
                servo_function_param="SERVO9_FUNCTION",
                servo_function_id=78,  # ArduPilot Function 78: V-Tail Right (Pitch - Yaw mixing)
                hardware_servo=servo_model,
                pwm_min_us=1000,
                pwm_neutral_us=1500,
                pwm_max_us=2000,
                pwm_trim_us=1500,
                protocol=OutputProtocol.DIGITAL_PWM_333HZ,
                signal_frequency_hz=333.0,
                direction_reversed=False,
                direction_verification_status=FlightControlStatus.GROUND_TEST_REQUIRED,
                hinge_torque_status=FlightControlStatus.DEFERRED,
                notes="Starboard empennage control surface. Inverted V-tail geometry requires sign check.",
            ),
        ]
        return servos
