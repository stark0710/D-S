"""
VTOL Tail Constraints Subsystem

Purpose:
    Defines the `TailConstraints` class storing physical ranges for tail sizing.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TailConstraints:
    """
    Limits on tail volume coefficients and physical span.

    Attributes:
        min_horizontal_volume_coefficient (float): Lower bound for Vh.
        max_horizontal_volume_coefficient (float): Upper bound for Vh.
        min_vertical_volume_coefficient (float): Lower bound for Vv.
        max_vertical_volume_coefficient (float): Upper bound for Vv.
        max_tail_span_m (float): Maximum physical horizontal tail width.
        metadata (Dict[str, Any]): Additional regulatory limits.
    """

    min_horizontal_volume_coefficient: float = 0.30
    max_horizontal_volume_coefficient: float = 0.90
    min_vertical_volume_coefficient: float = 0.02
    max_vertical_volume_coefficient: float = 0.08
    max_tail_span_m: float = 1.8
    metadata: Dict[str, Any] = field(default_factory=dict)
