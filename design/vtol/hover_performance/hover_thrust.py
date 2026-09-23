from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class HoverThrust:
    """
    Evaluates hover thrust margins and disk loading.
    """
    total_disk_area_m2: float
    disk_loading_n_m2: float
    thrust_margin_ratio: float  # T/W ratio
    thrust_ige_watts: float
    thrust_oge_watts: float
    ground_effect_thrust_gain_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
