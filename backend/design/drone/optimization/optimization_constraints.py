"""
OptimizationConstraints Subsystem

Purpose:
    Defines the `OptimizationConstraints` domain model representing optimization search space constraints.

Role in Architecture:
    `OptimizationConstraints` specifies hard MTOW upper bound, max battery capacity limit, and max frame wheelbase limit.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OptimizationConstraints:
    """
    Multirotor design optimization search space constraints.

    Attributes:
        max_mtow_kg (float): Maximum allowable MTOW limit in kg (default 25.0 kg).
        max_battery_capacity_mah (float): Maximum battery pack capacity limit in mAh (default 30000 mAh).
        max_wheelbase_mm (float): Maximum frame wheelbase in mm (default 1200 mm).
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_mtow_kg: float = 25.0
    max_battery_capacity_mah: float = 30000.0
    max_wheelbase_mm: float = 1200.0
    metadata: dict[str, Any] = field(default_factory=dict)
