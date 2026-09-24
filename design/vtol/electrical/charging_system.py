"""
VTOL Charging System Subsystem

Purpose:
    Defines the `ChargingAnalysis` class computing charging schedules.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ChargingAnalysis:
    """
    Sized battery balance charging times.

    Attributes:
        charging_current_a (float): Sized current during standard balance charging.
        charging_time_hr (float): Calculated recharge time in hours.
        recommended_charge_rate_c (float): Recommended charging rate in C-rate.
        balancer_active (bool): True if cell balancer is active.
        metadata (Dict[str, Any]): Thermal limits of charging.
    """

    charging_current_a: float
    charging_time_hr: float
    recommended_charge_rate_c: float
    balancer_active: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
