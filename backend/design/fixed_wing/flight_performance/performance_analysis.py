"""
Fixed-Wing Flight Performance Analysis Subsystem

Purpose:
    Defines the `PerformanceAnalysis` class.

Role in Architecture:
    `PerformanceAnalysis` holds maximum speed, cruise speed, minimum controllable speed, and rate of climb.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class PerformanceAnalysis:
    """
    General flight speeds and limits.

    Attributes:
        maximum_speed_kmh (float): Sized top speed at full throttle.
        cruise_speed_kmh (float): Cruise speed.
        minimum_controllable_speed_kmh (float): Safe minimum airspeed.
        best_glide_ratio (float): L/D max glide ratio.
        max_rate_of_climb_m_s (float): Peak climb rate capability.
        metadata (Dict[str, Any]): Speed ranges.
    """

    maximum_speed_kmh: float
    cruise_speed_kmh: float
    minimum_controllable_speed_kmh: float
    best_glide_ratio: float
    max_rate_of_climb_m_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
