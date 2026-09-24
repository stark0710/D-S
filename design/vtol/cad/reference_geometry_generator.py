from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ReferencePlane:
    """
    Reference planar surface.
    """
    name: str
    normal_vector: List[float]
    offset_mm: float

@dataclass(slots=True)
class ReferenceGeometry:
    """
    Reference planes, axes, and construction datum coordinate limits.
    """
    planes: List[ReferencePlane]
    axes_descriptions: List[str]
    origin_point_mm: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
