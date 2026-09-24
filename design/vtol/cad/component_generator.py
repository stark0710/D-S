from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PartModel:
    """
    Discrete CAD model part definition.
    """
    part_id: str
    file_path: str
    volume_mm3: float
    surface_area_mm2: float
    material_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
