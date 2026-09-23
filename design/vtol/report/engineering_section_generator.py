from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class EngineeringSection:
    """
    Structural and geometry choices description.
    """
    title: str
    materials_summary: str
    geometry_table: Dict[str, str]
    system_description: str
