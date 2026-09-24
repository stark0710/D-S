"""
VTOL Airfoil Constraints Subsystem

Purpose:
    Defines the `AirfoilConstraints` class bounding aerodynamic moments and thicknesses.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class AirfoilConstraints:
    """
    Limits on zero-lift pitching moments, drag coefficients, and thickness ratios.

    Attributes:
        max_pitching_moment_cm0 (float): Maximum nose-down pitching moment.
        min_thickness_ratio (float): Minimum thickness ratio for spar packaging.
        max_drag_coefficient_cd0 (float): Maximum zero-lift drag coefficient.
        metadata (Dict[str, Any]): Additional operational limits.
    """

    max_pitching_moment_cm0: float = -0.15
    min_thickness_ratio: float = 0.08
    max_drag_coefficient_cd0: float = 0.025
    metadata: Dict[str, Any] = field(default_factory=dict)
