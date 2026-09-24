"""
VTOL Tail Sizing Profile Subsystem

Purpose:
    Defines the `TailProfile` class storing safety margins and target coefficients.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TailProfile:
    """
    Standard references for tail sizing calculations.

    Attributes:
        default_horizontal_volume_coefficient (float): Horizontal tail volume target (Vh).
        default_vertical_volume_coefficient (float): Vertical tail volume target (Vv).
        safety_factor (float): Safety margin multiplier.
        metadata (Dict[str, Any]): Additional operational ranges.
    """

    default_horizontal_volume_coefficient: float = 0.55
    default_vertical_volume_coefficient: float = 0.045
    safety_factor: float = 1.5
    metadata: Dict[str, Any] = field(default_factory=dict)
