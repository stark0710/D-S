"""
VTOL Mass Profile Sizing Parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class MassProfile:
    """
    Reference metrics and default values for mass properties evaluation.
    """
    structural_weight_margin_pct: float = 10.0
    wiring_weight_fraction: float = 0.05
    fasteners_weight_fraction: float = 0.03
    default_empty_mass_fraction: float = 0.60
    metadata: Dict[str, Any] = field(default_factory=dict)
