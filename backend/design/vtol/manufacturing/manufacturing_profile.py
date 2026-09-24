"""
VTOL Manufacturing Profile parameters
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class ManufacturingProfile:
    """
    Labor rates, tooling costs, and certification standards (e.g. AS9100).
    """
    labor_rate_usd_per_hour: float = 65.0
    quality_standard: str = "AS9100"
    tooling_depreciation_factor: float = 0.1
    overhead_markup_ratio: float = 0.15
    metadata: Dict[str, Any] = field(default_factory=dict)
