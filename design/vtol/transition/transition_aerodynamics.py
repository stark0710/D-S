from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class AerodynamicAnalysis:
    """
    Sized lift transfers and wing lift build-up speeds.
    """
    wing_lift_growth_coefficient: float
    lift_transfer_duration_s: float
    stall_speed_calculated_kmh: float
    drag_peak_during_conversion_n: float
    metadata: Dict[str, Any] = field(default_factory=dict)
