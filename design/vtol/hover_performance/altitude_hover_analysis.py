from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class AltitudeHoverAnalysis:
    """
    Sized ceilings under variable atmospheric density.
    """
    density_ratio_at_ceiling: float
    hover_ceiling_ige_m: float
    hover_ceiling_oge_m: float
    hot_high_thrust_margin_ratio: float
    metadata: Dict[str, Any] = field(default_factory=dict)
