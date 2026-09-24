"""
PayloadConstraints Subsystem

Purpose:
    Defines the `PayloadConstraints` domain model representing payload integration design constraints.

Role in Architecture:
    `PayloadConstraints` specifies max payload physical dimensions (L, W, H mm), max CG offset in mm,
    and max payload electrical power consumption limit in Watts.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadConstraints:
    """
    Multirotor payload integration engineering design constraints.

    Attributes:
        max_dimensions_mm (tuple[float, float, float]): Max physical envelope (L, W, H) in mm.
        max_cg_offset_mm (float): Max allowed longitudinal/lateral CG offset in mm.
        max_payload_power_w (float): Max electrical power consumption limit in Watts.
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_dimensions_mm: tuple[float, float, float] = (400.0, 400.0, 400.0)
    max_cg_offset_mm: float = 25.0
    max_payload_power_w: float = 50.0
    metadata: dict[str, Any] = field(default_factory=dict)
