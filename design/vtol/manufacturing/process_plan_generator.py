from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ProcessOperation:
    """
    A fabrication operation (e.g., layup, milling, routing).
    """
    operation_id: str
    workcenter: str  # Composite Shop, Machine Shop, Electronics Bench
    description: str
    run_time_hours: float

@dataclass(slots=True)
class ManufacturingProcessPlan:
    """
    Manufacturing routing plan.
    """
    operations: List[ProcessOperation]
    total_lead_time_days: float
    metadata: Dict[str, Any] = field(default_factory=dict)
