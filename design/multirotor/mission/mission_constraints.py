from dataclasses import dataclass

@dataclass(slots=True)
class MissionConstraints:
    """
    Physical and economic constraints derived for the multirotor mission.
    """
    maximum_frame_size_m: float
    wind_resistance_limit_kmh: float
    minimum_ground_clearance_m: float
    cost_limit_usd: float
