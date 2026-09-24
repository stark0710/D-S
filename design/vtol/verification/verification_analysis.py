"""
VTOL Verification Analysis Aggregator
"""
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class VerificationAnalysis:
    overall_compliance_score_pct: float
    estimated_mtbf_hours: float
    is_fully_compliant: bool
    safety_index: float
    operational_readiness_score_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
