"""
Fixed-Wing Propulsion Climb Analysis Subsystem

Purpose:
    Defines the `ClimbAnalysis` class and sizing calculations.

Role in Architecture:
    `ClimbAnalysis` evaluates rate of climb (ROC), climb angle, and climb excess power.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class ClimbAnalysis:
    """
    Climb flight regime propulsion metrics.

    Attributes:
        rate_of_climb_m_s (float): Vertical climb rate in meters per second.
        climb_angle_deg (float): Flight path angle during climb in degrees.
        excess_power_w (float): Excess power available for climbing.
        time_to_altitude_min (float): Sized duration in minutes to reach target altitude.
        metadata (Dict[str, Any]): Intermediate lift, drag, and climb speed metrics.
    """

    rate_of_climb_m_s: float
    climb_angle_deg: float
    excess_power_w: float
    time_to_altitude_min: float
    metadata: Dict[str, Any] = field(default_factory=dict)
