from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class VerificationSection:
    """
    Safety checking checks.
    """
    title: str
    reliability_metrics: Dict[str, str]
    oei_capabilities: str
    compliance_score_pct: float
