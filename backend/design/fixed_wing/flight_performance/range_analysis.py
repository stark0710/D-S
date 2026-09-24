"""
Fixed-Wing Range Performance Analysis Subsystem

Purpose:
    Defines the `RangeAnalysis` class.

Role in Architecture:
    `RangeAnalysis` holds maximum range predictions and energy depletion rates.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class RangeAnalysis:
    """
    Flight range performance metrics.

    Attributes:
        maximum_range_km (float): Sized max travel range at optimal cruise.
        cruise_range_km (float): Safe operational range.
        energy_consumption_rate_wh_km (float): Energy depleted per kilometer.
        metadata (Dict[str, Any]): Battery/fuel capacity references.
    """

    maximum_range_km: float
    cruise_range_km: float
    energy_consumption_rate_wh_km: float
    metadata: Dict[str, Any] = field(default_factory=dict)
