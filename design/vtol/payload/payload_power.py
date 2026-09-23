from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PayloadPower:
    """
    Electrical distribution parameters.
    """
    continuous_power_watts: float
    peak_power_watts: float
    voltage_volts: float
    required_current_amps: float
    fuse_rating_amps: float
    power_source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
