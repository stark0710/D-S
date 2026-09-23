"""
Fixed-Wing Aerodynamic Performance Analysis Subsystem

Purpose:
    Defines the `AerodynamicAnalysis` class.

Role in Architecture:
    `AerodynamicAnalysis` holds lift/drag ratios, lift coefficients, and drag polars.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class AerodynamicAnalysis:
    """
    Aerodynamic lift and drag coefficients.

    Attributes:
        cruise_lift_coefficient (float): Sized lift coefficient.
        cruise_drag_coefficient (float): Sized drag coefficient.
        lift_to_drag_ratio (float): Aerodynamic lift-to-drag efficiency (L/D).
        zero_lift_drag_coefficient (float): Sectional parasite drag (Cd0).
        induced_drag_factor (float): Induced drag coefficient factor (K).
        metadata (Dict[str, Any]): Intermediate Reynolds polars.
    """

    cruise_lift_coefficient: float
    cruise_drag_coefficient: float
    lift_to_drag_ratio: float
    zero_lift_drag_coefficient: float
    induced_drag_factor: float
    metadata: Dict[str, Any] = field(default_factory=dict)
