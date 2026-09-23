"""
VTOL Mass Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class MassConstraints:
    """
    Structural stability and longitudinal static bounds.
    """
    max_takeoff_weight_kg: float = 80.0
    min_static_margin: float = 0.05  # minimum 5% static margin for stability
    max_cg_shift_pct_mac: float = 8.0
    allowed_cg_range_x_pct_mac_min: float = 0.15  # 15% MAC
    allowed_cg_range_x_pct_mac_max: float = 0.35  # 35% MAC
    allowed_cg_range_y_m: float = 0.02  # max 2cm lateral offset
    metadata: Dict[str, Any] = field(default_factory=dict)
