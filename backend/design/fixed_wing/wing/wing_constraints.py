"""
Fixed-Wing Wing Sizing Constraints Subsystem

Purpose:
    Defines the `WingConstraints` class to hold physical bounds.

Role in Architecture:
    `WingConstraints` groups structural limits and operational safety envelopes
    (e.g., maximum wingspan restrictions, aspect ratio limits) derived from user/regulatory bounds.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class WingConstraints:
    """
    Consolidated physical and structural constraints for the wing assembly.

    Attributes:
        max_wingspan_m (float | None): Maximum wingspan limit (e.g. from regulatory or hangar constraints).
        min_aspect_ratio (float): Lower bound for Aspect Ratio.
        max_aspect_ratio (float): Upper bound for Aspect Ratio.
        min_wing_loading_kg_m2 (float): Lower bound for wing loading in kg/m2.
        max_wing_loading_kg_m2 (float): Upper bound for wing loading in kg/m2.
    """

    max_wingspan_m: float | None
    min_aspect_ratio: float
    max_aspect_ratio: float
    min_wing_loading_kg_m2: float
    max_wing_loading_kg_m2: float
    min_root_chord_m: float | None = None
