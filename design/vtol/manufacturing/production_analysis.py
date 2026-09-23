from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ManufacturabilityAssessment:
    """
    Manufacturability complexity scores.
    """
    manufacturability_score_pct: float
    material_utilization_pct: float
    estimated_scrap_rate_pct: float
    assembly_complexity_index: float
    is_manufacturable: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
