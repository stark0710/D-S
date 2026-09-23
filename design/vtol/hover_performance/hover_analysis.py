"""
VTOL Hover Analysis Aggregator
"""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class HoverAnalysis:
    thrust_margin: float
    power_loading: float
    control_margin: float
    hover_ceiling_m: float
    wind_tolerance_kts: float
    thermal_load_factor: float
    metadata: Dict[str, Any] = field(default_factory=dict)
