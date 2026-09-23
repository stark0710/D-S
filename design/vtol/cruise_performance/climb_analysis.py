from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ClimbAnalysis:
    """
    Rates of climb and maximum angle sizing.
    """
    max_rate_of_climb_m_s: float
    max_climb_angle_deg: float
    time_to_ceiling_s: float
    climb_power_required_watts: float
    metadata: Dict[str, Any] = field(default_factory=dict)
