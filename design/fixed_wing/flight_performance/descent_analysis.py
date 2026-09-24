"""
Fixed-Wing Descent Performance Analysis Subsystem

Purpose:
    Defines the `DescentAnalysis` class.

Role in Architecture:
    `DescentAnalysis` holds sink rates, descent angles, and descent speeds.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class DescentAnalysis:
    """
    Descent flight performance metrics.

    Attributes:
        rate_of_descent_m_s (float): Sink rate (vertical descent speed) in meters per second.
        descent_angle_deg (float): Descent path angle.
        descent_speed_m_s (float): Forward airspeed during descent.
        metadata (Dict[str, Any]): Drag and gravity vectors.
    """

    rate_of_descent_m_s: float
    descent_angle_deg: float
    descent_speed_m_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
