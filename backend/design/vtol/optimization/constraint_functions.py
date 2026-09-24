from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ConstraintViolation:
    """
    A single constraint boundary violation.
    """
    name: str
    limit_value: float
    actual_value: float
    penalty_applied: float

@dataclass(slots=True)
class ConstraintSummary:
    """
    Violations overview list.
    """
    violations: List[ConstraintViolation]
    is_feasible: bool
    total_penalty: float
    metadata: Dict[str, Any] = field(default_factory=dict)
