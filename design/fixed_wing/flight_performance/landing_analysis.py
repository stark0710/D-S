"""
Fixed-Wing Landing Performance Analysis Subsystem

Purpose:
    Defines the `LandingAnalysis` class.

Role in Architecture:
    `LandingAnalysis` holds braking roll distances, approach velocities, and deceleration run times.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class LandingAnalysis:
    """
    Landing flight performance metrics.

    Attributes:
        landing_distance_m (float): Sized ground braking roll length in meters.
        approach_speed_m_s (float): Velocity at flare/approach threshold.
        braking_deceleration_m_s2 (float): Deceleration rate.
        landing_duration_s (float): Duration of runway braking roll.
        metadata (Dict[str, Any]): Braking frictions.
    """

    landing_distance_m: float
    approach_speed_m_s: float
    braking_deceleration_m_s2: float
    landing_duration_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
