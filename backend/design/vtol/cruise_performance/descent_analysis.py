from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class DescentAnalysis:
    """
    Rates of descent and glide ratios.
    """
    nominal_descent_rate_m_s: float
    best_glide_ratio: float
    emergency_descent_rate_m_s: float
    descent_angle_deg: float
    metadata: Dict[str, Any] = field(default_factory=dict)
