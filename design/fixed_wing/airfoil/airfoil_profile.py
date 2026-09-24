"""
Fixed-Wing Airfoil Sizing Profile Subsystem

Purpose:
    Defines the `AirfoilProfile` class, which holds constraints and analysis limits.

Role in Architecture:
    The profile is used to configure safety margins, Reynolds number ranges,
    and threshold limits during airfoil polar analysis.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AirfoilProfile:
    """
    Configuration profile defining limits and margins for airfoil polar checking.

    Attributes:
        reynolds_safety_margin (float): Multiplier to check Reynolds envelope bounds (default 1.1).
        stall_angle_margin_deg (float): Minimum margin between stall angle and cruise angle of attack (default 3.0 deg).
        max_absolute_c_m (float): Maximum acceptable absolute pitching moment coefficient (C_m0) (default 0.15).
        min_thickness_ratio (float): Lower bound for wing root thickness percentage (default 0.06).
    """

    reynolds_safety_margin: float = 1.1
    stall_angle_margin_deg: float = 3.0
    max_absolute_c_m: float = 0.15
    min_thickness_ratio: float = 0.06
