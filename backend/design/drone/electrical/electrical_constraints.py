"""
ElectricalConstraints Subsystem

Purpose:
    Defines the `ElectricalConstraints` domain model representing multirotor electrical safety and capacity constraints.

Role in Architecture:
    `ElectricalConstraints` specifies max battery weight in grams, min ESC current safety margin %,
    min battery discharge C-rate margin %, and energy reserve safety % (default 20%).
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ElectricalConstraints:
    """
    Multirotor electrical design safety and capacity constraints.

    Attributes:
        max_battery_weight_g (float): Maximum battery pack mass in grams.
        min_esc_current_margin_percent (float): Minimum ESC continuous current safety margin % over peak motor current (default 25%).
        min_discharge_c_margin_percent (float): Minimum battery C-rate safety margin % (default 30%).
        safety_reserve_percent (float): Battery energy reserve percentage for safe landing (default 20%).
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_battery_weight_g: float = 2500.0
    min_esc_current_margin_percent: float = 25.0
    min_discharge_c_margin_percent: float = 30.0
    safety_reserve_percent: float = 20.0
    metadata: dict[str, Any] = field(default_factory=dict)
