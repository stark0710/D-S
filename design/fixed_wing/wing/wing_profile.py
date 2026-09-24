"""
Fixed-Wing Wing Sizing Profile Subsystem

Purpose:
    Defines the `WingProfile` class, which holds geometry boundaries and optimization weights.

Role in Architecture:
    The profile is used to customize bounds for aspect ratio, wing loading limits,
    and relative importance coefficients during wing shape selection.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class WingProfile:
    """
    Configuration profile defining physical parameters and safety limits for wing sizing.

    Attributes:
        min_aspect_ratio (float): Minimum allowable aspect ratio (default 4.0).
        max_aspect_ratio (float): Maximum allowable aspect ratio (default 22.0).
        min_wing_loading_kg_m2 (float): Minimum wing loading (default 2.0 kg/m2).
        max_wing_loading_kg_m2 (float): Maximum wing loading (default 80.0 kg/m2).
        default_structural_factor (float): Factor representing material density/wing thickness multiplier (default 1.0).
    """

    min_aspect_ratio: float = 4.0
    max_aspect_ratio: float = 22.0
    min_wing_loading_kg_m2: float = 2.0
    max_wing_loading_kg_m2: float = 80.0
    default_structural_factor: float = 1.0
