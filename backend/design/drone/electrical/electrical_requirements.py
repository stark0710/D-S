"""
ElectricalRequirements Subsystem

Purpose:
    Defines the `ElectricalRequirements` domain model representing input requirements for electrical power design.

Role in Architecture:
    `ElectricalRequirements` specifies operating voltage in Volts, target flight endurance in minutes,
    total hover current in Amperes, and peak current in Amperes.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ElectricalRequirements:
    """
    Multirotor electrical engineering requirements model.

    Attributes:
        required_voltage_v (float): Target operating DC voltage in Volts.
        target_flight_time_min (float): Target mission flight time in minutes.
        total_hover_current_a (float): Required hover current draw in Amperes.
        total_max_current_a (float): Required peak current draw in Amperes.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    required_voltage_v: float = 22.2
    target_flight_time_min: float = 20.0
    total_hover_current_a: float = 30.0
    total_max_current_a: float = 90.0
    metadata: dict[str, Any] = field(default_factory=dict)
