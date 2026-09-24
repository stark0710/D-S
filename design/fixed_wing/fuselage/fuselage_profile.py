"""
Fixed-Wing Fuselage Sizing Profile Subsystem

Purpose:
    Defines the `FuselageProfile` class, which holds geometric tolerances and packaging margins.

Role in Architecture:
    The profile is used to configure safety clearances around internal components,
    default fineness ratios, and landing gear mount clearances.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class FuselageProfile:
    """
    Configuration profile defining tolerances and ratios for fuselage design.

    Attributes:
        clearance_margin_m (float): Minimum spacing around batteries and payloads in meters (default 0.005 m = 5mm).
        default_fineness_ratio (float): Ratio of fuselage length to height/width (default 6.5).
        min_fineness_ratio (float): Lower bound for fineness ratio (default 4.0).
        max_fineness_ratio (float): Upper bound for fineness ratio (default 12.0).
        cooling_duct_area_m2 (float): Target cooling intake duct area in square meters (default 0.0002).
    """

    clearance_margin_m: float = 0.005
    default_fineness_ratio: float = 6.5
    min_fineness_ratio: float = 4.0
    max_fineness_ratio: float = 12.0
    cooling_duct_area_m2: float = 0.0002
