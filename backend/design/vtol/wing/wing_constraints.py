"""
VTOL Wing Constraints Subsystem

Purpose:
    Defines the `WingConstraints` class storing geometric limits on wings.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class WingConstraints:
    """
    Limits on wingspan, aspect ratio, and wing loading.

    Attributes:
        min_aspect_ratio (float): Lower bound for aspect ratio.
        max_aspect_ratio (float): Upper bound for aspect ratio.
        min_wing_loading_kg_m2 (float): Lower bound for wing loading.
        max_wing_loading_kg_m2 (float): Upper bound for wing loading.
        max_wingspan_m (float): Maximum allowable span.
        metadata (Dict[str, Any]): Detailed boundary settings.
    """

    min_aspect_ratio: float = 5.0
    max_aspect_ratio: float = 18.0
    min_wing_loading_kg_m2: float = 10.0
    max_wing_loading_kg_m2: float = 120.0
    max_wingspan_m: float = 5.5
    metadata: Dict[str, Any] = field(default_factory=dict)
