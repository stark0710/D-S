from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class EnduranceAnalysis:
    """
    Sized endurances and reserve times.
    """
    estimated_endurance_min: float
    specific_endurance_min_kwh: float
    endurance_margin_pct: float
    reserve_endurance_capacity_min: float
    metadata: Dict[str, Any] = field(default_factory=dict)
