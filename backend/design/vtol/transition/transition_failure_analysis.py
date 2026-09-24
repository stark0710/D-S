from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class FailureAnalysis:
    """
    Evaluates one-motor out (OEI) and flight abort safe return trajectories.
    """
    oei_conversion_safety_status: bool
    abort_decision_airspeed_kmh: float
    recovery_glide_distance_m: float
    actuator_saturation_safety_margin_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
