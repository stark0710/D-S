"""
VTOL Forward Thrust Sizing Analysis Subsystem

Purpose:
    Defines the `ForwardPropulsionAnalysis` class capturing thrust and temperature parameters.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ForwardPropulsionAnalysis:
    """
    Cruise and static thrust performance parameters of the forward propulsion.

    Attributes:
        required_thrust_n (float): Drag force opposing cruise flight (Newtons).
        available_thrust_n (float): Sized maximum thrust at cruise speed (Newtons).
        static_thrust_n (float): Sized static thrust generated during ground bench tests.
        noise_level_db (float): Sized acoustic pressure signature.
        thermal_temperature_c (float): Estimated continuous motor operational temperature.
        metadata (Dict[str, Any]): Intermediate aerodynamics coefficients.
    """

    required_thrust_n: float
    available_thrust_n: float
    static_thrust_n: float
    noise_level_db: float
    thermal_temperature_c: float
    metadata: Dict[str, Any] = field(default_factory=dict)
