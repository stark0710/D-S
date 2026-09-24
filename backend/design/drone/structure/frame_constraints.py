"""
FrameConstraints Subsystem

Purpose:
    Defines the `FrameConstraints` domain model representing multirotor structural design constraints.

Role in Architecture:
    `FrameConstraints` specifies upper wheelbase bounds, minimum tip-to-tip propeller clearance in mm,
    minimum ground clearance in mm, and structural safety factor.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FrameConstraints:
    """
    Multirotor frame engineering design constraints model.

    Attributes:
        max_wheelbase_mm (float): Maximum allowed motor-to-motor wheelbase in mm.
        min_propeller_clearance_mm (float): Minimum required tip-to-tip propeller blade clearance in mm (e.g. 25mm).
        min_ground_clearance_mm (float): Minimum required ground clearance in mm.
        target_safety_factor (float): Minimum structural yield safety factor (e.g. 2.5).
        metadata (dict[str, Any]): Additional frame constraints metadata.
    """

    max_wheelbase_mm: float = 1400.0
    min_propeller_clearance_mm: float = 25.0
    min_ground_clearance_mm: float = 120.0
    target_safety_factor: float = 2.5
    metadata: dict[str, Any] = field(default_factory=dict)
