from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class RangeAnalysis:
    """
    Sized ranges, specific ranges, and battery limits.
    """
    estimated_range_km: float
    specific_range_km_kwh: float
    range_margin_pct: float
    reserve_range_capacity_km: float
    metadata: Dict[str, Any] = field(default_factory=dict)
