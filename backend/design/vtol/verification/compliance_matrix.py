from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ComplianceItem:
    """
    Checked item properties.
    """
    requirement_name: str
    required_value: str
    actual_value: str
    status: str  # Verified, Warning, Failed

@dataclass(slots=True)
class ComplianceMatrix:
    """
    Requirements checklist matching actuals vs limits.
    """
    checklist: List[ComplianceItem]
    compliance_score_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
