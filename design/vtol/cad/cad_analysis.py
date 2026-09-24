from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class InterferenceReport:
    """
    Summary of parts collisions.
    """
    interfering_parts: List[tuple[str, str]]
    total_interference_volume_mm3: float
    max_penetration_mm: float
    is_interference_free: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class ClearanceReport:
    """
    Summary of clearances preserved.
    """
    critical_clearance_parts: List[tuple[str, str]]
    actual_clearance_mm: float
    required_clearance_mm: float
    is_clearance_safe: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
