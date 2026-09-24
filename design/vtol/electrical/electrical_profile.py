"""
VTOL Electrical Profile Subsystem

Purpose:
    Defines the `ElectricalProfile` class storing material properties
    and resistance indexes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ElectricalProfile:
    """
    Standard references for battery pack resistance and voltage.

    Attributes:
        nominal_cell_voltage_v (float): Voltage baseline per cell (e.g. 3.7V).
        nominal_cell_capacity_ah (float): Sized capacity per cell (e.g. 5.0 Ah).
        default_wire_resistance_mohm_m (float): Specific resistance of 10AWG silicon power wires.
        metadata (Dict[str, Any]): Additional electrical benchmarks.
    """

    nominal_cell_voltage_v: float = 3.7
    nominal_cell_capacity_ah: float = 5.0
    default_wire_resistance_mohm_m: float = 3.2  # 10AWG copper wire resistance
    metadata: Dict[str, Any] = field(default_factory=dict)
