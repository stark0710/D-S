"""
Fixed-Wing Stall Performance Analysis Subsystem

Purpose:
    Defines the `StallAnalysis` class.

Role in Architecture:
    `StallAnalysis` holds clean and landing stall airspeeds and stall angles.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class StallAnalysis:
    """
    aerodynamic stall speed metrics.

    Attributes:
        stall_speed_clean_kmh (float): Stall speed in standard cruise configuration.
        stall_speed_landing_kmh (float): Stall speed with full flaps deflection.
        stall_angle_of_attack_deg (float): Sectional wing stall angle.
        stall_characteristics_warning (str): Textual warning description.
        metadata (Dict[str, Any]): Lift coefficients.
    """

    stall_speed_clean_kmh: float
    stall_speed_landing_kmh: float
    stall_angle_of_attack_deg: float
    stall_characteristics_warning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
