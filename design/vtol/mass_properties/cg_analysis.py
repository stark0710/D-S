from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class CenterOfGravity:
    """
    Aircraft CG location coordinates.
    """
    x_m: float
    y_m: float
    z_m: float
    x_pct_mac: float

@dataclass(slots=True)
class CGEnvelope:
    """
    Valid stability limits envelope.
    """
    forward_limit_x_m: float
    forward_limit_x_pct: float
    aft_limit_x_m: float
    aft_limit_x_pct: float
    lateral_limit_y_m: float
    fit_status: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
