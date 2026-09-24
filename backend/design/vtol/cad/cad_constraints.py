"""
VTOL CAD Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class CADConstraints:
    """
    clearances and physical interference bounds.
    """
    min_rotor_clearance_mm: float = 50.0  # 5cm rotor clearance
    min_battery_box_volume_mm3: float = 500000.0
    max_interference_volume_mm3: float = 0.0
    min_clearance_fit_mm: float = 2.0
    metadata: Dict[str, Any] = field(default_factory=dict)
