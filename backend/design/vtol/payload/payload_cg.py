from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PayloadCG:
    """
    Composite shift in aircraft Center of Gravity.
    """
    payload_cg_x_m: float
    payload_cg_y_m: float
    payload_cg_z_m: float
    aircraft_base_cg_x_m: float
    aircraft_base_cg_y_m: float
    aircraft_base_cg_z_m: float
    composite_cg_x_m: float
    composite_cg_y_m: float
    composite_cg_z_m: float
    cg_shift_x_m: float
    cg_shift_y_m: float
    cg_shift_z_m: float
    cg_shift_pct_mac: float
    metadata: Dict[str, Any] = field(default_factory=dict)
