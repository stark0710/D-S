from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class HoverPower:
    """
    Evaluates hover induced power and voltage sag effects.
    """
    induced_power_watts: float
    profile_power_watts: float
    total_hover_power_watts: float
    power_loading_n_w: float
    voltage_sag_multiplier: float
    metadata: Dict[str, Any] = field(default_factory=dict)
