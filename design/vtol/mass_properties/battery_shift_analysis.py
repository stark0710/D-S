from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class BatteryShiftAnalysis:
    """
    Analyzes layout corrections by shifting physical batteries or movable weight rails.
    """
    battery_base_x_m: float
    battery_optimum_x_m: float
    rail_travel_required_m: float
    counterbalance_capable: bool
    estimated_correction_x_pct_mac: float
    metadata: Dict[str, Any] = field(default_factory=dict)
