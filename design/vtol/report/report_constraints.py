"""
VTOL Report Constraints
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class ReportConstraints:
    """
    Mandatory checklist and section count validations.
    """
    min_required_sections_count: int = 7
    require_requirements_traceability: bool = True
    require_executive_summary: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
