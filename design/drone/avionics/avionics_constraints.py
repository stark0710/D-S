"""
AvionicsConstraints Subsystem

Purpose:
    Defines the `AvionicsConstraints` domain model representing multirotor avionics design constraints.

Role in Architecture:
    `AvionicsConstraints` specifies max avionics power consumption in Watts, max avionics weight in grams,
    min UART port requirement, and dual/triple IMU sensor redundancy requirements.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AvionicsConstraints:
    """
    Multirotor avionics subsystem design constraints.

    Attributes:
        max_avionics_power_w (float): Maximum power budget limit for avionics subsystem in Watts.
        max_avionics_weight_g (float): Maximum mass budget limit for avionics subsystem in grams.
        min_uart_ports (int): Minimum required free hardware UART ports (default 4).
        require_dual_imu (bool): True if dual/triple IMU sensor redundancy is required.
        metadata (dict[str, Any]): Additional constraints metadata.
    """

    max_avionics_power_w: float = 35.0
    max_avionics_weight_g: float = 800.0
    min_uart_ports: int = 4
    require_dual_imu: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
