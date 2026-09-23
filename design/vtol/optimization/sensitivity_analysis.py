from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class SensitivityAnalysis:
    """
    Local variable gradient changes.
    """
    wing_span_sensitivity_range: float
    rotor_diameter_sensitivity_endurance: float
    battery_weight_sensitivity_efficiency: float
    most_sensitive_variable: str
    metadata: Dict[str, Any] = field(default_factory=dict)
