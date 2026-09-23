"""
Fixed-Wing Horizontal Tail Geometry Subsystem

Purpose:
    Defines the `HorizontalTail` class holding horizontal stabilizer sized geometry parameters.

Role in Architecture:
    `HorizontalTail` is a pure domain entity storing horizontal dimensions
    like root/tip chord, sweep, aspect ratio, area, and wingspan.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class HorizontalTail:
    """
    Sized geometry parameters for the horizontal stabilizer.

    Attributes:
        area_m2 (float): Sized horizontal tail reference area in square meters.
        span_m (float): Sized horizontal tail span tip-to-tip in meters.
        chord_root_m (float): Horizontal tail root chord in meters.
        chord_tip_m (float): Horizontal tail tip chord in meters.
        aspect_ratio (float): Aspect ratio of the horizontal stabilizer.
        sweep_angle_deg (float): Horizontal tail sweep angle in degrees.
        taper_ratio (float): Taper ratio (tip_chord / root_chord).
        incidence_angle_deg (float): Stabilizer incidence angle relative to fuselage in degrees.
    """

    area_m2: float
    span_m: float
    chord_root_m: float
    chord_tip_m: float
    aspect_ratio: float
    sweep_angle_deg: float
    taper_ratio: float
    incidence_angle_deg: float
