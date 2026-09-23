from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PowerVerification:
    """
    continuous and peak rating budgets.
    """
    continuous_power_margin_watts: float
    peak_current_draw_amps: float
    voltage_sag_limit_verified: bool
    is_power_verified: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
