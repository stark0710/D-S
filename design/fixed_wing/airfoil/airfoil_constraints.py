"""
Fixed-Wing Airfoil Constraints Subsystem

Purpose:
    Defines the `AirfoilConstraints` class to hold operational boundaries.

Role in Architecture:
    `AirfoilConstraints` collects the aerodynamic limits (pitching moment, thickness ratios)
    and Reynolds boundaries to constraint selector lookup bounds.
"""

from dataclasses import dataclass, field
from typing import List
from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilType


@dataclass(slots=True)
class AirfoilConstraints:
    """
    Sizing bounds restricting selection of root and tip airfoils.

    Attributes:
        allowed_types (List[AirfoilType]): Aerodynamic classes permitted.
        max_pitching_moment_magnitude (float): Maximum absolute pitching moment limit.
        min_thickness_to_chord (float): Minimum allowable thickness-to-chord ratio (t/c).
        max_thickness_to_chord (float): Maximum allowable thickness-to-chord ratio (t/c).
        target_reynolds_min (float): Minimum expected flight Reynolds number.
        target_reynolds_max (float): Maximum expected flight Reynolds number.
    """

    allowed_types: List[AirfoilType] = field(default_factory=list)
    max_pitching_moment_magnitude: float = 0.15
    min_thickness_to_chord: float = 0.07
    max_thickness_to_chord: float = 0.18
    target_reynolds_min: float = 50000.0
    target_reynolds_max: float = 1000000.0
