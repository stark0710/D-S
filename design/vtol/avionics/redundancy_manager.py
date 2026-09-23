from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class RedundancyAnalysis:
    """
    Analyzes hardware redundancy and MTTF.
    """
    dual_gps_active: bool
    sensor_voting_active: bool
    flight_controller_redundancy: str
    power_input_redundancy: bool
    can_bus_redundancy: bool
    hardware_fault_tolerance_level: int
    estimated_mttf_hours: float
    metadata: Dict[str, Any] = field(default_factory=dict)
