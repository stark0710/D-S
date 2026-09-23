"""
ManeuverabilityAnalysis Subsystem

Purpose:
    Defines the `ManeuverabilityAnalysis` class for pitch, roll, and yaw dynamic maneuvering authority evaluation.

Role in Architecture:
    `ManeuverabilityAnalysis` evaluates angular acceleration capabilities (rad/s^2) across pitch, roll, and yaw axes.
"""

from typing import Any


class ManeuverabilityAnalysis:
    """
    Analysis service for multirotor dynamic maneuverability.

    Design Principles:
        - Single Responsibility Principle: Pitch/roll/yaw angular acceleration authority calculations only.
    """

    def analyze_maneuverability(
        self,
        rotor_count: int,
        arm_length_mm: float,
        max_thrust_per_motor_g: float,
        ixx_kg_m2: float,
        iyy_kg_m2: float,
        izz_kg_m2: float
    ) -> dict[str, float]:
        """
        Calculates maximum angular accelerations in rad/s^2.

        Args:
            rotor_count (int): Total rotor count.
            arm_length_mm (float): Arm length in mm.
            max_thrust_per_motor_g (float): Max thrust per motor in grams.
            ixx_kg_m2 (float): Roll MoI.
            iyy_kg_m2 (float): Pitch MoI.
            izz_kg_m2 (float): Yaw MoI.

        Returns:
            dict[str, float]: Maneuverability dictionary.
        """
        arm_m = arm_length_mm / 1000.0
        max_thrust_n = (max_thrust_per_motor_g / 1000.0) * 9.80665

        # Maximum differential thrust torque T_pitch = (N/4) * F_max * L_arm
        max_torque_pitch = (rotor_count / 4.0) * max_thrust_n * arm_m
        max_torque_roll = (rotor_count / 4.0) * max_thrust_n * arm_m
        max_torque_yaw = max_torque_pitch * 0.20  # Reaction torque ~20%

        alpha_pitch = max_torque_pitch / iyy_kg_m2 if iyy_kg_m2 > 0 else 5.0
        alpha_roll = max_torque_roll / ixx_kg_m2 if ixx_kg_m2 > 0 else 5.0
        alpha_yaw = max_torque_yaw / izz_kg_m2 if izz_kg_m2 > 0 else 2.0

        return {
            "max_pitch_angular_accel_rad_s2": round(alpha_pitch, 1),
            "max_roll_angular_accel_rad_s2": round(alpha_roll, 1),
            "max_yaw_angular_accel_rad_s2": round(alpha_yaw, 1),
        }
