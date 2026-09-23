"""
VTOL Verification Profile Sizing parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class VerificationProfile:
    """
    Standard confidence ratings and certification references.
    """
    confidence_level_pct: float = 95.0
    mtbf_target_hours: float = 100.0
    certification_category: str = "Civil Light UAV"
    safety_factor: float = 1.5
    metadata: Dict[str, Any] = field(default_factory=dict)
