from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class WindHoverAnalysis:
    """
    Sized crosswind thrust limits and yaw deflection boundaries.
    """
    crosswind_limit_kts: float
    gust_tolerance_kts: float
    yaw_deflection_margin_pct: float
    aerodynamic_heave_offset_n: float
    metadata: Dict[str, Any] = field(default_factory=dict)
