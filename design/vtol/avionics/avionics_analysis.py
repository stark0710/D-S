from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class AvionicsAnalysis:
    """
    Evaluated performance metrics for the avionics selection.
    """
    navigation_accuracy_rating: float
    sensor_redundancy_level: int
    bus_utilization_pct: float
    cpu_utilization_pct: float
    memory_utilization_pct: float
    power_consumption_watts: float
    autonomy_capability_score: float
    reliability_score: float
    fault_tolerance_score: float
    maintainability_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
