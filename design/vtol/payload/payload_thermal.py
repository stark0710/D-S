from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class PayloadThermal:
    """
    Thermal limits and active airflow cooling needs.
    """
    heat_generated_watts: float
    cooling_type: str
    airflow_cfm_required: float
    operating_temperature_max_c: float
    cooling_margin_c: float
    metadata: Dict[str, Any] = field(default_factory=dict)
