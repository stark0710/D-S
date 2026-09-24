from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class AutonomyStack:
    """
    Autonomy algorithms configured on the companion computer and flight controller.
    """
    waypoint_navigation_active: bool
    obstacle_avoidance_active: bool
    precision_landing_active: bool
    vision_based_navigation_active: bool
    geofencing_active: bool
    terrain_following_active: bool
    return_to_land_failsafe: bool
    autonomy_level: int
    metadata: Dict[str, Any] = field(default_factory=dict)
