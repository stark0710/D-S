from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class QualityCheckpoint:
    """
    A quality checkpoint check.
    """
    checkpoint_id: str
    operation_stage: str
    inspection_method: str  # Ultrasonic, Visual, Continuity
    tolerance_bounds: str

@dataclass(slots=True)
class QualityPlan:
    """
    Certification quality gates.
    """
    checkpoints: List[QualityCheckpoint]
    pass_criteria_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
