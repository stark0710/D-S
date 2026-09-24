from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class ToolingItem:
    """
    composite molds or milling tools.
    """
    tool_id: str
    tool_type: str  # Mold, CNC Bit, Autoclave Bag
    cost_usd: float
    reusable_cycles: int

@dataclass(slots=True)
class ToolingPlan:
    """
    Tool tooling setups.
    """
    tooling_list: List[ToolingItem]
    total_tooling_cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)
