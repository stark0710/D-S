from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class FailureHoverAnalysis:
    """
    Sizes one-engine-out (OEI) margins and emergency vertical landing descent paths.
    """
    oei_thrust_margin_ratio: float
    oei_control_headroom_pct: float
    is_safe_under_failure: bool
    emergency_descent_rate_m_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
