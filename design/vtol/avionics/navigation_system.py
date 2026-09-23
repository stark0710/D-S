from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class NavigationSystem:
    """
    EKF configuration and position estimation details.
    """
    fusion_algorithm: str
    rtk_active: bool
    rtk_accuracy_m: float
    vision_positioning_active: bool
    dead_reckoning_capable: bool
    sensor_voting_active: bool
    gps_heading_active: bool
    estimated_position_accuracy_m: float
    estimated_heading_accuracy_deg: float
    metadata: Dict[str, Any] = field(default_factory=dict)
