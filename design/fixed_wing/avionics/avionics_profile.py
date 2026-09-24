"""
Fixed-Wing Avionics Sizing Profile Subsystem

Purpose:
    Defines the `AvionicsProfile` class, which holds safety margins and firmware parameters.

Role in Architecture:
    The profile is used to configure telemetry link margins, flight controller CPU safety thresholds,
    and GNSS redundancy counts.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AvionicsProfile:
    """
    Configuration profile defining limits and redundances for autopilot systems.

    Attributes:
        telemetry_safety_margin (float): Multiplier for link budget calculations (default 1.25).
        max_cpu_load_limit (float): Upper bound for flight controller CPU usage (default 0.75).
        min_redundancy_level (int): Minimum required GNSS receiver count (default 1).
        visual_odometry_enabled (bool): Flag indicating if companion computers handle visual navigation.
    """

    telemetry_safety_margin: float = 1.25
    max_cpu_load_limit: float = 0.75
    min_redundancy_level: int = 1
    visual_odometry_enabled: bool = False
