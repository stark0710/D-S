"""
VTOL Battery Pack Sizing Analysis Subsystem

Purpose:
    Defines the `BatteryAnalysis` class evaluating internal resistances and cycle lifes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class BatteryAnalysis:
    """
    Rotor voltage sags and cycle life ratings.

    Attributes:
        voltage_sag_v (float): Voltage drop under peak hover current.
        peak_current_margin_percent (float): Margin between available peak current and max hover current draw.
        hover_c_rate (float): Hover discharge rate.
        cruise_c_rate (float): Cruise discharge rate.
        battery_efficiency (float): Sized conversion efficiency (due to heat losses).
        estimated_cycle_life (int): Estimated charging lifecycles count.
        metadata (Dict[str, Any]): Additional operational margins.
    """

    voltage_sag_v: float
    peak_current_margin_percent: float
    hover_c_rate: float
    cruise_c_rate: float
    battery_efficiency: float
    estimated_cycle_life: int
    metadata: Dict[str, Any] = field(default_factory=dict)
