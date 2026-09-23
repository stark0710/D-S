from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PerformanceVerification:
    """
    Evaluates hover, transition, and cruise performance margins.
    """
    hover_performance_score_pct: float
    transition_performance_score_pct: float
    cruise_performance_score_pct: float
    average_performance_score_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
