from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PayloadBay:
    """
    Physical dimensions and fit clearances.
    """
    width_m: float
    height_m: float
    length_m: float
    max_load_kg: float
    bay_volume_m3: float
    fit_status: bool
    clearance_x_m: float
    clearance_y_m: float
    clearance_z_m: float
    metadata: Dict[str, Any] = field(default_factory=dict)
