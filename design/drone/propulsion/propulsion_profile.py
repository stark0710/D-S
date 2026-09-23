"""
PropulsionProfile Subsystem

Purpose:
    Defines the `PropulsionProfile` domain model representing multirotor propulsion subsystem specifications.

Role in Architecture:
    `PropulsionProfile` encapsulates motor model, motor KV rating, motor max power, propeller diameter/pitch,
    rotor count, and coaxial configuration flag.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PropulsionProfile:
    """
    Multirotor propulsion subsystem specification profile.

    Attributes:
        motor_model (str): Motor model string (e.g. 'BLDC Stator 3510').
        motor_kv (float): Motor KV rating (RPM/V).
        motor_max_power_w (float): Maximum motor power in Watts.
        propeller_size_inch (str): Propeller size string (e.g. '13.0x4.5').
        propeller_diameter_inch (float): Propeller diameter in inches.
        propeller_pitch_inch (float): Propeller pitch in inches.
        motor_count (int): Total motor count.
        coaxial (bool): True if coaxial configuration.
        metadata (dict[str, Any]): Additional propulsion metadata.
    """

    motor_model: str
    motor_kv: float
    motor_max_power_w: float
    propeller_size_inch: str
    propeller_diameter_inch: float
    propeller_pitch_inch: float
    motor_count: int
    coaxial: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
