"""
VTOL Fuselage Constraints Subsystem

Purpose:
    Defines the `FuselageConstraints` class storing geometric boundaries.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class FuselageConstraints:
    """
    Limits on fuselage lengths, volumes, and center-of-gravity offsets.

    Attributes:
        min_length_m (float): Lower limit for fuselage length.
        max_length_m (float): Upper limit for fuselage length.
        min_volume_m3 (float): Lower limit for internal packing volume.
        max_cg_offset_mac_percent (float): Allowable CG offset distance from wing MAC center.
        metadata (Dict[str, Any]): Additional regulatory limits.
    """

    min_length_m: float = 0.5
    max_length_m: float = 3.5
    min_volume_m3: float = 0.005
    max_cg_offset_mac_percent: float = 10.0
    metadata: Dict[str, Any] = field(default_factory=dict)
