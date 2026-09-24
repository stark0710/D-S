"""
PropulsionRequirements Subsystem

Purpose:
    Defines the `PropulsionRequirements` domain model representing input requirements for propulsion engineering.

Role in Architecture:
    `PropulsionRequirements` specifies total required thrust in grams, required thrust per motor in grams,
    target thrust-to-weight ratio, and operating voltage in Volts.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PropulsionRequirements:
    """
    Multirotor propulsion engineering requirements model.

    Attributes:
        total_required_thrust_g (float): Total required maximum thrust in grams.
        required_thrust_per_motor_g (float): Target maximum thrust per motor in grams.
        target_thrust_to_weight_ratio (float): Target T/W ratio (default 2.0).
        target_voltage_v (float): Operating voltage in Volts (default 22.2V).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    total_required_thrust_g: float
    required_thrust_per_motor_g: float
    target_thrust_to_weight_ratio: float = 2.0
    target_voltage_v: float = 22.2
    metadata: dict[str, Any] = field(default_factory=dict)
