"""
Fixed-Wing Avionics Navigation Analysis Subsystem

Purpose:
    Defines the `NavigationAnalysis` class.

Role in Architecture:
    `NavigationAnalysis` evaluates GPS/RTK redundancy levels, compass counts,
    and visual positioning backup modes.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class NavigationAnalysis:
    """
    Navigation and autopilot redundancy metrics.

    Attributes:
        gnss_type (str): GNSS level (RTK RTK GNSS, Standard).
        redundancy_level (int): Number of active GPS units (e.g. 2 for Dual GPS).
        waypoint_mission_support (bool): Flag indicating full automatic grid waypoints.
        visual_navigation_capable (bool): Flag indicating companion computer optical flow.
        estimated_cpu_load_pct (float): Estimated flight controller CPU usage.
        metadata (Dict[str, Any]): Intermediate IMU/Baro sensors.
    """

    gnss_type: str
    redundancy_level: int
    waypoint_mission_support: bool
    visual_navigation_capable: bool
    estimated_cpu_load_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
