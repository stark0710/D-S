"""
VTOL Manufacturing Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class ManufacturingConstraints:
    """
    Budgets and lead times.
    """
    max_production_cost_usd: float = 15000.0
    max_assembly_time_hours: float = 100.0
    min_manufacturability_score_pct: float = 75.0
    min_material_utilization_pct: float = 80.0
    metadata: Dict[str, Any] = field(default_factory=dict)
