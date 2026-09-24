from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PropulsionAnalysis:
    """
    Rotor unloading parameters and propeller synchronization.
    """
    rotor_unloading_speed_kmh: float
    propeller_sync_efficiency_pct: float
    lift_motor_shutdown_speed_kmh: float
    peak_thrust_delivered_n: float
    metadata: Dict[str, Any] = field(default_factory=dict)
