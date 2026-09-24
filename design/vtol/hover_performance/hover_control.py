from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class HoverControl:
    """
    Sized angular control accelerations and deflection margins.
    """
    roll_authority_rad_s2: float
    pitch_authority_rad_s2: float
    yaw_authority_rad_s2: float
    control_headroom_pct: float
    has_sufficient_authority: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
