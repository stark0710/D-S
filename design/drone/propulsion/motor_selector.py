"""
MotorSelector Subsystem

Purpose:
    Defines the `MotorSelector` class responsible for sizing and selecting motor engineering specifications.

Role in Architecture:
    `MotorSelector` determines motor stator class size (e.g. 2207, 2806, 3510, 5010, 8318), KV rating,
    voltage rating, max power rating, and weight estimate from thrust requirements.
"""

from typing import Any


class MotorSelector:
    """
    Selection service for multirotor motor engineering specifications.

    Design Principles:
        - Single Responsibility Principle: Motor stator class, KV, and power sizing only.
    """

    def select_motor(
        self,
        hover_thrust_per_motor_g: float,
        max_thrust_per_motor_g: float,
        voltage_v: float = 22.2
    ) -> dict[str, Any]:
        """
        Determines optimal motor engineering parameters.

        Args:
            hover_thrust_per_motor_g (float): Hover thrust per motor in grams.
            max_thrust_per_motor_g (float): Max thrust per motor in grams.
            voltage_v (float): Nominal operating voltage in Volts.

        Returns:
            dict[str, Any]: Selected motor specifications dictionary.
        """
        # Sizing heuristic by max thrust per motor
        if max_thrust_per_motor_g > 6000.0:
            stator = "8318"
            kv = 100
            weight_g = 650.0
            max_p_w = 2200.0
        elif max_thrust_per_motor_g > 3500.0:
            stator = "5010"
            kv = 300
            weight_g = 220.0
            max_p_w = 1100.0
        elif max_thrust_per_motor_g > 2000.0:
            stator = "3510"
            kv = 600
            weight_g = 120.0
            max_p_w = 650.0
        elif max_thrust_per_motor_g > 1000.0:
            stator = "2806"
            kv = 1300
            weight_g = 55.0
            max_p_w = 400.0
        else:
            stator = "2207"
            kv = 1800
            weight_g = 34.0
            max_p_w = 250.0

        return {
            "motor_class": f"BLDC Stator {stator}",
            "stator_size": stator,
            "kv_rating": kv,
            "operating_voltage_v": voltage_v,
            "max_power_w": max_p_w,
            "estimated_motor_weight_g": weight_g,
            "recommended_hover_thrust_g": hover_thrust_per_motor_g,
            "recommended_max_thrust_g": max_thrust_per_motor_g,
        }
