"""
VTOL Redundant Power Subsystem

Purpose:
    Defines the `RedundantSupply` and `RedundantPower` classes modeling backup BECs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class RedundantSupply:
    """
    Sized backup power unit.

    Attributes:
        name (str): Backup BEC name.
        switchover_time_ms (float): Time delay before failover BEC takes over the bus.
        voltage_v (float): Voltage level.
        backup_capacity_ah (float): Sized capacity.
    """

    name: str
    switchover_time_ms: float
    voltage_v: float
    backup_capacity_ah: float


@dataclass(slots=True)
class RedundantPower:
    """
    Consolidated fail-safe power configurations.

    Attributes:
        supplies (List[RedundantSupply]): Individual backup BEC rails.
        has_dual_bus_isolation (bool): True if avionics buses are electrically isolated from ESC noise.
        metadata (Dict[str, Any]): Redundancy notes.
    """

    supplies: List[RedundantSupply]
    has_dual_bus_isolation: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
