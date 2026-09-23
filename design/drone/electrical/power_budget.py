"""
PowerBudget Subsystem

Purpose:
    Defines the `PowerBudget` domain model and service for multirotor electrical power budgeting.

Role in Architecture:
    `PowerBudget` breaks down total system power consumption across propulsion motors, avionics flight controllers,
    telemetry radios, and mission payload sensors.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PowerBudget:
    """
    Multirotor electrical power budget breakdown model.

    Attributes:
        propulsion_hover_power_w (float): Hover propulsion power draw in Watts.
        propulsion_peak_power_w (float): Peak propulsion power draw in Watts.
        avionics_power_w (float): Flight controller, receiver, GPS power draw in Watts (default 15W).
        payload_power_w (float): Camera, gimbal, sensor payload power draw in Watts (default 10W).
        total_hover_power_w (float): Total system hover power draw in Watts.
        total_peak_power_w (float): Total system peak power draw in Watts.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    propulsion_hover_power_w: float
    propulsion_peak_power_w: float
    avionics_power_w: float = 15.0
    payload_power_w: float = 10.0
    total_hover_power_w: float = 0.0
    total_peak_power_w: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Computes total hover and peak power values."""
        if self.total_hover_power_w == 0.0:
            self.total_hover_power_w = round(self.propulsion_hover_power_w + self.avionics_power_w + self.payload_power_w, 1)
        if self.total_peak_power_w == 0.0:
            self.total_peak_power_w = round(self.propulsion_peak_power_w + self.avionics_power_w + self.payload_power_w, 1)
