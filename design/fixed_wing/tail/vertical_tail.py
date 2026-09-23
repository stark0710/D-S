"""
Fixed-Wing Vertical Tail Geometry Subsystem

Purpose:
    Defines the `VerticalTail` class holding vertical stabilizer sized geometry parameters.

Role in Architecture:
    `VerticalTail` is a pure domain entity storing vertical dimensions
    like root/tip chord, sweep, aspect ratio, area, and height.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class VerticalTail:
    """
    Sized geometry parameters for the vertical stabilizer.

    Attributes:
        area_m2 (float): Sized vertical tail reference area in square meters.
        height_m (float): Sized vertical tail height in meters.
        chord_root_m (float): Vertical tail root chord in meters.
        chord_tip_m (float): Vertical tail tip chord in meters.
        aspect_ratio (float): Aspect ratio of the vertical stabilizer.
        sweep_angle_deg (float): Vertical tail sweep angle in degrees.
        taper_ratio (float): Taper ratio (tip_chord / root_chord).
    """

    area_m2: float
    height_m: float
    chord_root_m: float
    chord_tip_m: float
    aspect_ratio: float
    sweep_angle_deg: float
    taper_ratio: float
