from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class TransitionDynamics:
    """
    Horizontal and vertical acceleration forces.
    """
    mean_forward_accel_m_s2: float
    thrust_vector_angle_deg: float
    altitude_loss_estimated_m: float
    time_to_stall_margin_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
