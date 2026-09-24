"""
VTOL Lift System Profile Subsystem

Purpose:
    Defines the `LiftSystemProfile` class storing safety limits and thermal coefficients.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class LiftSystemProfile:
    """
    Standard references for vertical lift calculations.

    Attributes:
        hover_thrust_safety_factor (float): Sizing multiplier (T_hover_max / MTOW_g).
        motor_max_temperature_c (float): Maximum allowed motor casing temperature.
        battery_nominal_voltage_v (float): Voltage baseline driving RPM Kv checks.
        metadata (Dict[str, Any]): Additional default references.
    """

    hover_thrust_safety_factor: float = 1.5
    motor_max_temperature_c: float = 80.0
    battery_nominal_voltage_v: float = 44.4
    metadata: Dict[str, Any] = field(default_factory=dict)
