"""
VTOL Power Distribution Subsystem

Purpose:
    Defines the `PowerBus` and `PowerDistribution` classes routing voltage rails.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class PowerBus:
    """
    Sized distribution power bus.

    Attributes:
        name (str): Bus identifier (e.g. 12S Main ESC Bus, 5V Avionics Rail).
        voltage_rail_v (float): Rail voltage.
        max_current_a (float): Maximum current capacity.
        subsystems_connected (List[str]): Subsystems attached to rail.
    """

    name: str
    voltage_rail_v: float
    max_current_a: float
    subsystems_connected: List[str]


@dataclass(slots=True)
class PowerDistribution:
    """
    Consolidated power distribution configurations.

    Attributes:
        buses (List[PowerBus]): Individual distribution buses.
        power_module_efficiency (float): Sized BEC/power module conversion efficiency.
        high_current_routing_awg (int): Sized gauge of main battery wires.
        metadata (Dict[str, Any]): Harness details.
    """

    buses: List[PowerBus]
    power_module_efficiency: float
    high_current_routing_awg: int
    metadata: Dict[str, Any] = field(default_factory=dict)
