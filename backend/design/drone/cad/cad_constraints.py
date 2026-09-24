"""
CADConstraints Subsystem

Purpose:
    Defines the `CADConstraints` domain model representing geometric CAD assembly constraints.

Role in Architecture:
    `CADConstraints` specifies maximum physical bounding box dimensions (L, W, H mm) and max component count limit.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CADConstraints:
    """
    Multirotor CAD generation geometric constraints.

    Attributes:
        max_bounding_box_mm (tuple[float, float, float]): Max physical envelope (Length, Width, Height) in mm.
        max_component_count (int): Maximum component count limit (default 100).
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_bounding_box_mm: tuple[float, float, float] = (2000.0, 2000.0, 1000.0)
    max_component_count: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)
