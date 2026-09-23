"""
DroneMissionConstraints Subsystem

Purpose:
    Defines the `DroneMissionConstraints` domain model representing multirotor physical and operational engineering constraints.

Role in Architecture:
    `DroneMissionConstraints` encapsulates max MTOW limits, max frame dimension bounds, min thrust-to-weight ratio,
    operating temperature range, and current draw boundaries.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DroneMissionConstraints:
    """
    Multirotor engineering design constraints model.

    Attributes:
        max_takeoff_weight_kg (float): Upper limit on Maximum Take-Off Weight (MTOW) in kg.
        max_dimensions_mm (float): Maximum diagonal motor-to-motor frame size limit in mm.
        min_thrust_to_weight_ratio (float): Minimum required thrust-to-weight ratio for control authority.
        max_current_draw_a (float): Upper current draw limit in Amperes.
        operating_temp_range (tuple[float, float]): Operating temperature envelope in °C.
        metadata (dict[str, Any]): Additional constraint diagnostic metadata.
    """

    max_takeoff_weight_kg: float
    max_dimensions_mm: float = 1200.0
    min_thrust_to_weight_ratio: float = 1.8
    max_current_draw_a: float = 200.0
    operating_temp_range: tuple[float, float] = (-10.0, 45.0)
    metadata: dict[str, Any] = field(default_factory=dict)
