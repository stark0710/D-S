"""
VTOL Avionics Constraints definitions
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass(slots=True)
class AvionicsConstraints:
    """
    Engineering constraints for validating avionics selection.
    """
    max_cpu_utilization_pct: float = 85.0
    max_memory_utilization_pct: float = 80.0
    max_power_consumption_watts: float = 100.0
    min_reliability_score: float = 0.90
    required_bus_redundancy: bool = False
    allowed_flight_controllers: List[str] = field(default_factory=lambda: [
        "Pixhawk 6X", "Pixhawk 6C", "Cube Orange", "CUAV V5+", "Holybro Durandal", "Auterion Skynode", "Custom Flight Controller"
    ])
    allowed_companion_computers: List[str] = field(default_factory=lambda: [
        "Raspberry Pi 4", "Jetson Nano", "Jetson Orin NX", "Jetson Xavier NX", "Intel NUC", "RK3588", "Custom Companion Computer"
    ])
    metadata: Dict[str, Any] = field(default_factory=dict)
