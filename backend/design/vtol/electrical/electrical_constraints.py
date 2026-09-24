"""
VTOL Electrical Constraints Subsystem

Purpose:
    Defines the `ElectricalConstraints` class storing safety margins.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ElectricalConstraints:
    """
    Limits on cell temperatures, voltage sags, and reserve power.

    Attributes:
        min_voltage_sag_v (float): Maximum allowed voltage drop under peak currents.
        max_cell_temp_c (float): Maximum cell temperature limits before thermal runaway.
        min_reserve_energy_fraction (float): Sized percentage of battery capacity reserved for emergencies.
        metadata (Dict[str, Any]): Additional regulatory limits.
    """

    min_voltage_sag_v: float = 4.0
    max_cell_temp_c: float = 60.0
    min_reserve_energy_fraction: float = 0.20
    metadata: Dict[str, Any] = field(default_factory=dict)
