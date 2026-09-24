"""
VTOL Hover Profile reference factors
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class HoverProfile:
    """
    Standard constants and parameters for hover aerodynamic equations.
    """
    ground_effect_reference_height_m: float = 1.20
    induced_power_correction_factor: float = 1.15
    profile_drag_power_fraction: float = 0.30
    battery_sag_offset_factor: float = 0.05
    rotor_interference_loss_pct: float = 8.0
    metadata: Dict[str, Any] = field(default_factory=dict)
