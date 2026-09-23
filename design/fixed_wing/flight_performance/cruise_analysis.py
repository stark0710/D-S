"""
Fixed-Wing Cruise Performance Analysis Subsystem

Purpose:
    Defines the `CruiseAnalysis` class.

Role in Architecture:
    `CruiseAnalysis` holds cruise speed, thrust/power requirements, and throttle levels.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class CruiseAnalysis:
    """
    Cruise flight performance metrics.

    Attributes:
        cruise_speed_kmh (float): Cruise speed.
        thrust_required_n (float): Aerodynamic drag opposing motion.
        power_required_w (float): Sized continuous shaft power.
        throttle_setting_pct (float): Autopilot throttle position.
        cruise_lift_coefficient (float): Sized wing lift coefficient.
        metadata (Dict[str, Any]): Dynamic pressure values.
    """

    cruise_speed_kmh: float
    thrust_required_n: float
    power_required_w: float
    throttle_setting_pct: float
    cruise_lift_coefficient: float
    metadata: Dict[str, Any] = field(default_factory=dict)
