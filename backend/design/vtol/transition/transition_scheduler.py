from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass(slots=True)
class FlightModeSchedule:
    """
    Triggers for switching control logic during conversion.
    """
    hover_phase_duration_s: float
    blended_phase_duration_s: float
    wing_borne_phase_duration_s: float
    lift_shutdown_airspeed_kmh: float

@dataclass(slots=True)
class TransitionSchedule:
    """
    Schedules throttle and control surface actions over transition timeline.
    """
    airspeed_steps_kmh: List[float]
    lift_throttle_percentage: List[float]
    forward_throttle_percentage: List[float]
    surface_control_effectiveness: List[float]
    flight_mode_schedule: FlightModeSchedule
    metadata: Dict[str, Any] = field(default_factory=dict)
