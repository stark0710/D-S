"""
Fixed-Wing Flight Performance Profile Subsystem

Purpose:
    Defines the `FlightProfile` class, which holds ISA constants and safety limits.

Role in Architecture:
    The profile is used to configure standard ground friction, temperature reference indices,
    and climb margins.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class FlightProfile:
    """
    Configuration profile defining limits and references for flight calculations.

    Attributes:
        ground_friction_coefficient (float): Runway wheel roll resistance coefficient (default 0.04).
        headwind_estimate_m_s (float): Assumed constant headwind during performance audits (default 0.0).
        climb_angle_safety_factor (float): Safety multiplier on excess climb rate power (default 1.15).
        gravity_m_s2 (float): Acceleration due to gravity (default 9.80665).
    """

    ground_friction_coefficient: float = 0.04
    headwind_estimate_m_s: float = 0.0
    climb_angle_safety_factor: float = 1.15
    gravity_m_s2: float = 9.80665
    braking_coefficient: float = 0.4
