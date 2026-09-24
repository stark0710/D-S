"""
VTOL Forward Propulsion Profile Subsystem

Purpose:
    Defines the `ForwardPropulsionProfile` class storing safety limits and thermal coefficients.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ForwardPropulsionProfile:
    """
    Standard references for forward flight propulsion calculations.

    Attributes:
        nominal_motor_efficiency (float): Sizing baseline drive train efficiency.
        nominal_propeller_efficiency (float): Baseline propulsive efficiency during cruise.
        air_density_sea_level (float): Density coefficient baseline.
        metadata (Dict[str, Any]): Additional default references.
    """

    nominal_motor_efficiency: float = 0.85
    nominal_propeller_efficiency: float = 0.70
    air_density_sea_level: float = 1.225
    metadata: Dict[str, Any] = field(default_factory=dict)
