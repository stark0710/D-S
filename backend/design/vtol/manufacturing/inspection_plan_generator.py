from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class InspectionItem:
    """
    An inspection item parameters.
    """
    parameter_name: str
    nominal_value: str
    actual_tolerance: str
    device_used: str

@dataclass(slots=True)
class InspectionPlan:
    """
    Inspection logs.
    """
    inspections: List[InspectionItem]
    inspector_level_required: str
    metadata: Dict[str, Any] = field(default_factory=dict)
