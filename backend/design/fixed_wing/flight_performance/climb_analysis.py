"""
Fixed-Wing Climb Performance Analysis Subsystem

Purpose:
    Defines the `ClimbAnalysis` class.

Role in Architecture:
    `ClimbAnalysis` holds climb rates, angles, and time to climb.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class ClimbAnalysis:
    """
    Climb flight performance metrics.

    Attributes:
        rate_of_climb_m_s (float): Vertical climb rate in meters per second.
        climb_angle_deg (float): Flight path angle.
        climb_speed_m_s (float): Sized forward airspeed during climb.
        time_to_altitude_min (float): Time required to reach target operational altitude.
        metadata (Dict[str, Any]): Power and thrust details.
    """

    rate_of_climb_m_s: float
    climb_angle_deg: float
    climb_speed_m_s: float
    time_to_altitude_min: float
    metadata: Dict[str, Any] = field(default_factory=dict)
