from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PayloadAnalysis:
    """
    Packaging efficiency, CG checks, and operational scores.
    """
    packaging_efficiency_pct: float
    accessibility_score: float
    cg_shift_pct: float
    structural_load_ratio: float
    power_consumption_pct: float
    thermal_load_ratio: float
    data_bandwidth_utilization_pct: float
    mission_suitability_score: float
    maintainability_rating: str
    metadata: Dict[str, Any] = field(default_factory=dict)
