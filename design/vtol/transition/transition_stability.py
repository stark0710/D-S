from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class StabilityAnalysis:
    """
    Longitudinal and lateral safety metrics during conversion.
    """
    min_stability_margin: float
    neutral_point_travel_m: float
    max_pitch_excursion_deg: float
    roll_damping_stability: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
