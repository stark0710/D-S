from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class StabilityVerification:
    """
    Verifies pitch/roll loops and aerodynamic centers.
    """
    static_margin_verified: bool
    hover_damping_verified: bool
    transition_stability_margin_pct: float
    is_stably_controllable: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
