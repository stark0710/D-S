from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ObjectiveValues:
    """
    Calculated optimization scoring indices.
    """
    endurance_score: float
    range_score: float
    weight_score: float
    efficiency_score: float
    reliability_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
