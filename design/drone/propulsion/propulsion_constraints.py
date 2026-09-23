"""
PropulsionConstraints Subsystem

Purpose:
    Defines the `PropulsionConstraints` domain model representing multirotor propulsion constraints.

Role in Architecture:
    `PropulsionConstraints` specifies max propeller diameter in inches, max current draw per motor in Amperes,
    min hover throttle percentage, and max hover throttle percentage.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PropulsionConstraints:
    """
    Multirotor propulsion engineering design constraints.

    Attributes:
        max_propeller_diameter_inch (float): Maximum propeller diameter allowed by frame clearance.
        max_current_draw_per_motor_a (float): Maximum current draw limit per motor in Amperes.
        min_hover_throttle_percent (float): Minimum hover throttle percentage (e.g. 35%).
        max_hover_throttle_percent (float): Upper allowable limit on hover throttle percentage (e.g. 60%).
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_propeller_diameter_inch: float = 18.0
    max_current_draw_per_motor_a: float = 60.0
    min_hover_throttle_percent: float = 35.0
    max_hover_throttle_percent: float = 60.0
    metadata: dict[str, Any] = field(default_factory=dict)
