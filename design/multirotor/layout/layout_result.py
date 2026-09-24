from dataclasses import dataclass, field
from typing import Dict, List

@dataclass(slots=True)
class LayoutSpecification:
    """
    Sized and optimized Component Packaging & Mounting Layout specification.
    """
    component_coordinates: Dict[str, tuple[float, float, float]]
    mounting_locations: Dict[str, str]
    cable_routing: Dict[str, str]
    payload_mount: str
    cooling_zones: List[str]
    maintenance_zones: List[str]
    accessibility_score: float
    packaging_efficiency_pct: float
    optimization_score: float
    engineering_reasoning: str
