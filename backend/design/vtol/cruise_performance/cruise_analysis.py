"""
VTOL Cruise Analysis Aggregator
"""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class CruiseAnalysis:
    cruise_speed_kmh: float
    range_km: float
    endurance_min: float
    max_rate_of_climb_m_s: float
    service_ceiling_m: float
    battery_reserve_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
