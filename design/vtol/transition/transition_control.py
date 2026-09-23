from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ControlSchedule:
    """
    Schedules control command allocations across conversion stages.
    """
    control_stages: List[str]
    rotor_weight_factors: List[float]
    surface_weight_factors: List[float]
    actuator_saturation_risk_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
