"""
VTOL Cruise Power Analysis Subsystem

Purpose:
    Defines the `CruisePowerAnalysis` class estimating cruise currents and electrical C-rates.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class CruisePowerAnalysis:
    """
    Electrical power metrics under forward flight cruise conditions.

    Attributes:
        required_cruise_power_w (float): Sized input electric power to cruise motors.
        current_draw_a (float): Total electrical current draw during wing-borne cruise.
        power_loading_w_kg (float): Sized power-to-weight ratio in W/kg.
        battery_c_rate (float): Nominal continuous C-rate discharge during cruise.
        metadata (Dict[str, Any]): Intermediate electrical parameters.
    """

    required_cruise_power_w: float
    current_draw_a: float
    power_loading_w_kg: float
    battery_c_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)
