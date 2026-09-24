"""
VTOL Battery Pack Configuration Subsystem

Purpose:
    Defines the `BatteryPack` class modeling cell packaging and weights.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class BatteryPack:
    """
    Sized physical battery pack configuration.

    Attributes:
        chemistry (str): Battery cell chemistry style (e.g. LiPo, Li-Ion).
        series_count_s (int): Count of cells placed in series.
        parallel_count_p (int): Count of cells placed in parallel.
        capacity_ah (float): Sized total pack capacity in Amp-hours.
        nominal_voltage_v (float): Sized nominal output pack voltage (S * nominal_cell_voltage).
        energy_wh (float): Sized total pack energy capacity (Wh).
        mass_kg (float): Sized physical pack weight (kg).
        continuous_current_limit_a (float): Sized safe continuous current limit (Amps).
        peak_current_limit_a (float): Sized peak current discharge limit (Amps).
        metadata (Dict[str, Any]): Cell dimension clearances.
    """

    chemistry: str
    series_count_s: int
    parallel_count_p: int
    capacity_ah: float
    nominal_voltage_v: float
    energy_wh: float
    mass_kg: float
    continuous_current_limit_a: float
    peak_current_limit_a: float
    metadata: Dict[str, Any] = field(default_factory=dict)
