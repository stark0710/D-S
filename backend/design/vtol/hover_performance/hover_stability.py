from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class HoverStability:
    """
    Attitude damping rates and wind gust response metrics.
    """
    roll_damping_rate_n_m_s: float
    pitch_damping_rate_n_m_s: float
    yaw_damping_rate_n_m_s: float
    rotor_interference_loss_pct: float
    gust_response_damping_ratio: float
    is_stably_damped: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
