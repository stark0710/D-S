"""
VTOL CAD Profile parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class CADProfile:
    """
    Geometric tolerances, reference offsets, and rendering standards.
    """
    tolerance_mm: float = 0.1
    default_mesh_density: str = "High"
    origin_offset_x_mm: float = 0.0
    origin_offset_y_mm: float = 0.0
    origin_offset_z_mm: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
