from dataclasses import dataclass, field
from typing import List, Dict, Any
from .design_variables import DesignVariable

@dataclass(slots=True)
class ParetoPoint:
    """
    A non-dominated design candidate.
    """
    variables: List[DesignVariable]
    objectives: List[float]  # e.g. [range, endurance, weight]
    crowding_distance: float

@dataclass(slots=True)
class ParetoFront:
    """
    Sized non-dominated Pareto Front front lists.
    """
    points: List[ParetoPoint]
    dimension_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
