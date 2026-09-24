from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class BOMItem:
    """
    A single part or fastener in the Bill of Materials.
    """
    part_number: str
    description: str
    quantity: int
    unit_cost_usd: float
    material: str
    category: str  # Structure, Propulsion, Electrical, Hardware

@dataclass(slots=True)
class BillOfMaterials:
    """
    Complete parts tree listing.
    """
    items: List[BOMItem]
    total_parts_count: int
    total_material_cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)
