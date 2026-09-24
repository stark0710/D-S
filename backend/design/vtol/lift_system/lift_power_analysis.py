"""
VTOL Lift System Power Analysis Subsystem

Purpose:
    Defines the `LiftPowerAnalysis` class estimating hover currents and battery C-rates.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class LiftPowerAnalysis:
    """
    Electrical power metrics under maximum hover conditions.

    Attributes:
        hover_total_power_kw (float): Sized power consumption during hover.
        hover_total_current_a (float): Total electrical current draw from the battery.
        hover_energy_consumption_kwh (float): Sized total energy consumption of hover stage.
        esc_current_draw_a (float): Current draw per individual ESC.
        battery_c_rate_required (float): Sized C-rate discharge capability needed.
        metadata (Dict[str, Any]): Intermediate electrical parameters.
    """

    hover_total_power_kw: float
    hover_total_current_a: float
    hover_energy_consumption_kwh: float
    esc_current_draw_a: float
    battery_c_rate_required: float
    metadata: Dict[str, Any] = field(default_factory=dict)
