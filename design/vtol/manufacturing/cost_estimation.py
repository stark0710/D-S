from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class ProductionCostEstimate:
    """
    Estimated production costs.
    """
    bill_of_materials_cost_usd: float
    labor_cost_usd: float
    tooling_amortized_cost_usd: float
    fixture_amortized_cost_usd: float
    overhead_cost_usd: float
    total_unit_cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)
