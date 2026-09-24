from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ManufacturingFeature:
    """
    Drills, taps, ventilation, or routing channels.
    """
    feature_type: str  # Hole, Slot, Vent, Latch
    associated_part: str
    coordinates_mm: List[float]
    diameter_or_width_mm: float
