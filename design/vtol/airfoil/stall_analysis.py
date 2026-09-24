"""
VTOL Airfoil Stall Analysis Subsystem

Purpose:
    Defines the `StallAnalysis` class evaluating maximum lift capability,
    stall angles, and rotor downwash velocity influences.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class StallAnalysis:
    """
    Stall characteristics analysis of the selected airfoil, considering downwash.

    Attributes:
        cl_max (float): Maximum lift coefficient.
        stall_angle_deg (float): Angle of attack at stall.
        downwash_velocity_m_s (float): Rotor-induced vertical downwash velocity.
        downwash_angle_deg (float): Effective angle deflection from rotor wash.
        stall_behavior (str): Description of stall behavior (e.g. Gentle, Progressive, Sharp).
        metadata (Dict[str, Any]): Additional stall metrics.
    """

    cl_max: float
    stall_angle_deg: float
    downwash_velocity_m_s: float
    downwash_angle_deg: float
    stall_behavior: str
    metadata: Dict[str, Any] = field(default_factory=dict)
