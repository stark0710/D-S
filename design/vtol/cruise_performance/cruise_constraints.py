"""
VTOL Cruise Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class CruiseConstraints:
    """
    Sustained cruise flight limits.
    """
    min_cruise_speed_kmh: float = 50.0
    min_range_km: float = 15.0
    min_endurance_min: float = 15.0
    min_climb_rate_m_s: float = 2.0
    max_cruise_power_watts: float = 15000.0
    min_battery_reserve_pct: float = 15.0
    metadata: Dict[str, Any] = field(default_factory=dict)
