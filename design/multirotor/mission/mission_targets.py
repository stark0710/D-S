from dataclasses import dataclass
from typing import Tuple

@dataclass(slots=True)
class MissionTargets:
    """
    Subsystem design and sizing targets derived from mission needs.
    """
    preferred_configuration_class: str
    preferred_frame_class: str
    target_thrust_to_weight_ratio: float
    target_hover_time_min: float
    target_cruise_time_min: float
    target_hover_stability: str
    preferred_battery_class: str
    preferred_propeller_class: str
    preferred_motor_kv_range: Tuple[float, float]
    preferred_redundancy: bool
    preferred_safety_margin: float
