from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class CruisePowerAnalysis:
    """
    Sized required drag, thrust, wattage, currents, and temperature loads.
    """
    drag_n: float
    thrust_required_n: float
    cruise_power_watts: float
    cruise_current_amps: float
    thermal_load_factor: float
    power_margin_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
