from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class TradeoffAnalysis:
    """
    Calculates compromise ratios between design priorities.
    """
    range_vs_mass_tradeoff_slope: float
    endurance_vs_efficiency_slope: float
    selected_compromise_index: int
    compromise_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
