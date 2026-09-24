from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ManufacturingSection:
    """
    BOM, tooling and price estimates.
    """
    title: str
    bom_cost_usd: float
    assembly_time_hours: float
    curing_plan_details: str
