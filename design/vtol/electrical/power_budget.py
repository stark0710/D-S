"""
VTOL Power Budget Subsystem

Purpose:
    Defines the `PowerBudgetSlot` and `PowerBudget` classes detailing power consumption.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class PowerBudgetSlot:
    """
    Sized power draws of a specific subsystem.

    Attributes:
        subsystem (str): Subsystem identifier (e.g. Avionics Autopilot, Lift Propulsion).
        hover_power_w (float): Power draw in watts during hover.
        cruise_power_w (float): Power draw in watts during cruise.
        transition_power_w (float): Power draw in watts during transition.
    """

    subsystem: str
    hover_power_w: float
    cruise_power_w: float
    transition_power_w: float


@dataclass(slots=True)
class PowerBudget:
    """
    Consolidated power draws across all flight states.

    Attributes:
        slots (List[PowerBudgetSlot]): Power draws for each subsystem.
        total_hover_w (float): Combined total hover power demand.
        total_cruise_w (float): Combined total cruise power demand.
        total_transition_w (float): Combined total transition power demand.
        reserve_energy_wh (float): reserve energy buffer.
        metadata (Dict[str, Any]): Additional power indices.
    """

    slots: List[PowerBudgetSlot]
    total_hover_w: float
    total_cruise_w: float
    total_transition_w: float
    reserve_energy_wh: float
    metadata: Dict[str, Any] = field(default_factory=dict)
