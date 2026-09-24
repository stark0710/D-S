from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ManeuverAnalysis:
    """
    Load factors and roll limits.
    """
    max_load_factor_g: float
    max_bank_angle_deg: float
    turn_radius_m: float
    roll_rate_limit_deg_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
