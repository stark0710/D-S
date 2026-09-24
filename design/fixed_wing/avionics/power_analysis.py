"""
Fixed-Wing Avionics Power Analysis Subsystem

Purpose:
    Defines the `PowerAnalysis` class.

Role in Architecture:
    `PowerAnalysis` evaluates continuous avionics power draw (FC + GPS + Telemetry + Sensors)
    and backup battery details.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class PowerAnalysis:
    """
    Electronics power consumption metrics.

    Attributes:
        continuous_power_w (float): continuous power draw of avionics.
        peak_power_w (float): Peak power draw under telemetry transmission.
        backup_power_supported (bool): Flag indicating if dual BEC power supplies exist.
        current_draw_5v_a (float): Sized current draw on 5V bus in Amps.
        metadata (Dict[str, Any]): Voltages and sensor powers.
    """

    continuous_power_w: float
    peak_power_w: float
    backup_power_supported: bool
    current_draw_5v_a: float
    metadata: Dict[str, Any] = field(default_factory=dict)
