"""
VTOL Airfoil Polar Analysis Subsystem

Purpose:
    Defines the `PolarAnalysis` class representing sectional lift, drag,
    and pitching moments under propeller slipstream corrections.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class PolarAnalysis:
    """
    Sectional polar performance analysis.

    Attributes:
        cl_cruise (float): Local lift coefficient required for cruise weight support.
        cd_cruise (float): Sectional drag coefficient under cruise conditions.
        lift_to_drag_ratio_sectional (float): Sectional aerodynamic efficiency.
        pitching_moment_cruise (float): Pitching moment coefficient at cruise.
        slipstream_correction_factor (float): Dynamic pressure scaling multiplier behind propellers.
        metadata (Dict[str, Any]): Detailed drag polar components.
    """

    cl_cruise: float
    cd_cruise: float
    lift_to_drag_ratio_sectional: float
    pitching_moment_cruise: float
    slipstream_correction_factor: float
    metadata: Dict[str, Any] = field(default_factory=dict)
