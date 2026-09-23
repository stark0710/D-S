from dataclasses import dataclass, field
from typing import Any, Tuple
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

@dataclass(slots=True)
class MissionProfile:
    """
    Normalized multirotor operational mission requirements profile.
    """
    mission_type: str
    payload_weight_kg: float
    payload_dimensions_m: Tuple[float, float, float]
    target_flight_time_min: float
    target_range_km: float
    cruise_speed_kmh: float
    operating_environment: str
    wind_conditions_kmh: float
    budget: float
    redundancy_required: bool
    maximum_frame_size_m: float
    battery_preference: str
    camera_requirement: str
    autonomy_level: str
    metadata: dict[str, Any] = field(default_factory=dict)
