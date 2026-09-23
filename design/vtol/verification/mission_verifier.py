from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class MissionVerification:
    """
    Evaluates profile timelines and success rate probabilities.
    """
    mission_success_probability_pct: float
    estimated_mission_completion_rate_pct: float
    takeoff_verified: bool
    landing_verified: bool
    is_mission_feasible: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
