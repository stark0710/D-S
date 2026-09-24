from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ParametricGeometry:
    """
    Calculated 3D bounding mesh specifications.
    """
    part_name: str
    vertex_count: int
    face_count: int
    bounding_box_width_mm: float
    bounding_box_height_mm: float
    bounding_box_depth_mm: float
    metadata: Dict[str, Any] = field(default_factory=dict)
