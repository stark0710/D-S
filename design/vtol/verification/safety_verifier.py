from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class SafetyVerification:
    """
    Evaluates abort speeds and clearance boundaries.
    """
    abort_safety_score_pct: float
    clearance_fit_status: bool
    g_load_margin_pct: float
    is_safety_verified: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
