"""
VTOL Verification Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class VerificationConstraints:
    """
    Certification safety compliance thresholds.
    """
    min_overall_compliance_score_pct: float = 90.0
    min_reliability_mtbf_hours: float = 100.0
    min_stability_safety_margin_pct: float = 15.0
    min_battery_reserve_sooc_pct: float = 10.0
    metadata: Dict[str, Any] = field(default_factory=dict)
