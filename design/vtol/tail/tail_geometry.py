"""
VTOL Tail Geometry Subsystem

Purpose:
    Defines the `TailGeometry` class storing structural tail dimensions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TailGeometry:
    """
    Sized geometry parameters for vertical and horizontal stabilizers.

    Attributes:
        tail_configuration (str): Tail layout class (Conventional, V-Tail, etc.).
        tail_arm_m (float): Distance from wing AC to tail AC.
        horizontal_area_m2 (float): Surface area of horizontal stabilizer.
        horizontal_span_m (float): Horizontal tail span.
        horizontal_aspect_ratio (float): Horizontal tail aspect ratio.
        vertical_area_m2 (float): Surface area of vertical stabilizer.
        vertical_span_m (float): Vertical stabilizer height/span.
        vertical_aspect_ratio (float): Vertical stabilizer aspect ratio.
        v_tail_angle_deg (float): V-tail dihedral angle (0 if conventional).
        metadata (Dict[str, Any]): Additional planform details.
    """

    tail_configuration: str
    tail_arm_m: float
    horizontal_area_m2: float
    horizontal_span_m: float
    horizontal_aspect_ratio: float
    vertical_area_m2: float
    vertical_span_m: float
    vertical_aspect_ratio: float
    v_tail_angle_deg: float
    metadata: Dict[str, Any] = field(default_factory=dict)
