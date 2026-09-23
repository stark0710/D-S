"""
VTOL Transition Profile parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class TransitionProfile:
    """
    Structural bounds and default configurations for conversion segments.
    """
    stall_speed_margin_pct: float = 20.0
    nominal_accel_m_s2: float = 1.5
    pitch_angle_limit_deg: float = 15.0
    deceleration_limit_m_s2: float = 1.2
    minimum_transition_altitude_m: float = 50.0
    metadata: Dict[str, Any] = field(default_factory=dict)
