"""
VTOL Airfoil Profile Subsystem

Purpose:
    Defines the `AirfoilProfile` class storing safety limits and Reynolds bounds
    used in sectional aerodynamic polars.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class AirfoilProfile:
    """
    Standard references for sectional polar lookups.

    Attributes:
        target_reynolds_number (float): Reference Reynolds number for cruise checks.
        reference_temperature_k (float): Base ambient temperature.
        reference_kinematic_viscosity (float): Base kinematic viscosity of standard air.
        metadata (Dict[str, Any]): Additional operational margins.
    """

    target_reynolds_number: float = 200000.0
    reference_temperature_k: float = 288.15
    reference_kinematic_viscosity: float = 1.48e-5
    metadata: Dict[str, Any] = field(default_factory=dict)
