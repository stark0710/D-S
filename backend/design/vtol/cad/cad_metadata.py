from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PartMetadata:
    """
    Non-geometric metadata parameters.
    """
    part_number: str
    revision: str
    designer: str
    weight_kg: float
    material_density_g_cm3: float
    metadata: Dict[str, Any] = field(default_factory=dict)
