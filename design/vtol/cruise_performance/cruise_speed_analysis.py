from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class CruiseSpeedAnalysis:
    """
    Sized cruise, endurance, range, max, and stall limits.
    """
    cruise_speed_kmh: float
    best_endurance_speed_kmh: float
    best_range_speed_kmh: float
    maximum_speed_kmh: float
    minimum_cruise_speed_kmh: float
    stall_speed_kmh: float
    metadata: Dict[str, Any] = field(default_factory=dict)
