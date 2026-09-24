"""
VTOL Cruise Profile Sizing parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class CruiseProfile:
    """
    Aero efficiency parameters and power transfer metrics.
    """
    nominal_lift_to_drag_ratio: float = 10.0
    propulsive_efficiency: float = 0.75
    battery_reserve_threshold_pct: float = 15.0
    motor_thermal_limit_c: float = 85.0
    structural_load_limit_g: float = 2.5
    metadata: Dict[str, Any] = field(default_factory=dict)
