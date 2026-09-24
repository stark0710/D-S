from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ReliabilityVerification:
    """
    Sized failure rates and Mean Time Between Failures.
    """
    estimated_mtbf_hours: float
    composite_failure_rate_per_hour: float
    redundancy_level_index: float
    is_reliability_verified: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
