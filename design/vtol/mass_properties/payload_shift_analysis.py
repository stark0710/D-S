from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PayloadShiftAnalysis:
    """
    Sizing shift deltas when payload is empty vs loaded.
    """
    dry_cg_x_m: float
    dry_cg_x_pct: float
    wet_cg_x_m: float
    wet_cg_x_pct: float
    shift_x_m: float
    shift_x_pct_mac: float
    is_safe: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
