"""
Fixed-Wing Mass Sizing Constraints Subsystem

Purpose:
    Defines the `MassConstraints` class to hold physical bounds.

Role in Architecture:
    `MassConstraints` collects maximum takeoff weights, static stability margins,
    and payload loading boundaries.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class MassConstraints:
    """
    Sizing bounds restricting weight budgets and aerodynamic stability limits.

    Attributes:
        max_takeoff_weight_kg (float): Upper physical limit on total loaded weight.
        max_empty_weight_kg (float): Limit on airframe structural mass.
        min_static_margin (float): Minimum stability reserve (as fraction of MAC, e.g. 0.08).
        max_static_margin (float): Maximum stability reserve (to avoid excessive nose-heaviness).
    """

    max_takeoff_weight_kg: float = 10.0
    max_empty_weight_kg: float = 5.0
    min_static_margin: float = 0.08
    max_static_margin: float = 0.22
