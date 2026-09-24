"""
VTOL Hover Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class HoverConstraints:
    """
    Performance limits for safe hover operations.
    """
    min_hover_thrust_margin_ratio: float = 1.30  # T/W ratio
    max_hover_power_watts: float = 45000.0
    min_control_authority_headroom_pct: float = 15.0
    max_wind_velocity_kts: float = 25.0
    min_oei_thrust_ratio: float = 1.0  # thrust margin with one motor out
    metadata: Dict[str, Any] = field(default_factory=dict)
