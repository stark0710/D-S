from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class HoverEfficiency:
    """
    Sized figure of merit and continuous energy usage.
    """
    figure_of_merit: float  # induced power vs total power
    energy_consumption_kwh_min: float
    hover_endurance_min: float
    metadata: Dict[str, Any] = field(default_factory=dict)
