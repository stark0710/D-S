"""
Fixed-Wing Fuselage Sizing Constraints Subsystem

Purpose:
    Defines the `FuselageConstraints` class to hold physical bounds.

Role in Architecture:
    `FuselageConstraints` collects the dimensional restrictions, allowed fuselage types,
    and volume parameters required for the sizer.
"""

from dataclasses import dataclass, field
from typing import List
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageType


@dataclass(slots=True)
class FuselageConstraints:
    """
    Sizing bounds restricting fuselage lengths, volumes, and allowed structures.

    Attributes:
        allowed_styles (List[FuselageType]): Permitted fuselage types.
        min_payload_volume_m3 (float): Minimum payload compartment volume.
        min_battery_volume_m3 (float): Minimum battery compartment volume.
        max_fuselage_length_m (float | None): Maximum structural length bound.
    """

    allowed_styles: List[FuselageType] = field(default_factory=list)
    min_payload_volume_m3: float = 0.001
    min_battery_volume_m3: float = 0.0005
    max_fuselage_length_m: float | None = None
