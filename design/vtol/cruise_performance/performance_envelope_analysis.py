from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PerformanceEnvelope:
    """
    Sized service and operational ceilings.
    """
    service_ceiling_m: float
    operational_ceiling_m: float
    maximum_altitude_limit_m: float
    is_within_envelope: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
