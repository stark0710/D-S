"""
Fixed-Wing Takeoff Performance Analysis Subsystem

Purpose:
    Defines the `TakeoffAnalysis` class.

Role in Architecture:
    `TakeoffAnalysis` holds ground roll distances, rotation velocities, and ground run times.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class TakeoffAnalysis:
    """
    Takeoff flight performance metrics.

    Attributes:
        takeoff_distance_m (float): Sized ground roll run length in meters.
        rotation_speed_m_s (float): Velocity at takeoff lift-off.
        ground_acceleration_m_s2 (float): Net acceleration rate on runway.
        takeoff_duration_s (float): Sized duration of takeoff run.
        metadata (Dict[str, Any]): Friction and thrust vectors.
    """

    takeoff_distance_m: float
    rotation_speed_m_s: float
    ground_acceleration_m_s2: float
    takeoff_duration_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
