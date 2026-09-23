from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class FlightModeManager:
    """
    Manages VTOL flight modes, transitions, and failsafes.
    """
    supported_modes: List[str]
    transition_logic_type: str
    mode_synchronization_active: bool
    failsafe_modes: List[str]
    can_command_rate_hz: float
    real_time_scheduler: str
    metadata: Dict[str, Any] = field(default_factory=dict)
