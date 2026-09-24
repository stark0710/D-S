"""
Fixed-Wing Propulsion Takeoff Analysis Subsystem

Purpose:
    Defines the `TakeoffAnalysis` class and sizing calculations.

Role in Architecture:
    `TakeoffAnalysis` evaluates takeoff distance, ground acceleration force, and rotation speed.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class TakeoffAnalysis:
    """
    Takeoff flight phase propulsion metrics.

    Attributes:
        takeoff_distance_m (float): Estimated horizontal takeoff roll distance in meters.
        takeoff_velocity_m_s (float): Velocity at takeoff rotation (typically 1.2 * V_stall).
        acceleration_force_n (float): Net forward force during ground run.
        takeoff_time_s (float): Estimated ground run time in seconds.
        metadata (Dict[str, Any]): Intermediate lift, drag, and friction coefficients.
    """

    takeoff_distance_m: float
    takeoff_velocity_m_s: float
    acceleration_force_n: float
    takeoff_time_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
