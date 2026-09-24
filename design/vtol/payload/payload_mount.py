from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PayloadMount:
    """
    Mechanical interface details for payload integration.
    """
    mount_type: str
    weight_kg: float
    power_draw_watts: float
    vibration_isolation: bool
    quick_release: bool
    drag_coefficient: float
    metadata: Dict[str, Any] = field(default_factory=dict)
