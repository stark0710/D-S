from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class MassPropertiesAnalysis:
    """
    Evaluates hover, transition, and cruise parameters.
    """
    hover_cg_offset_x_m: float  # distance to rotor center
    hover_cg_offset_y_m: float
    hover_balance_index: float  # 0.0 to 1.0 (perfectly symmetric)
    transition_neutral_point_x_m: float
    transition_static_margin: float
    cruise_static_margin: float
    structural_weight_margin_kg: float
    weight_growth_headroom_kg: float
    metadata: Dict[str, Any] = field(default_factory=dict)
