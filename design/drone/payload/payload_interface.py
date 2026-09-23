"""
PayloadInterface Subsystem

Purpose:
    Defines the `PayloadInterface` domain model representing electrical and data link interface specifications.

Role in Architecture:
    `PayloadInterface` specifies power supply voltage in Volts, power connector type, data communications protocol,
    and required bandwidth in Mbps.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadInterface:
    """
    Multirotor payload electrical and data interface definition.

    Attributes:
        power_voltage_v (float): Required power supply voltage in Volts (e.g. 12.0V or 24.0V).
        power_connector (str): Electrical power connector specification (e.g. 'XT30 / JST-XH').
        data_protocol (str): Data interface protocol (e.g. 'Ethernet IP / MAVLink / USB-C').
        required_bandwidth_mbps (float): Required data link bandwidth in Mbps.
        metadata (dict[str, Any]): Additional interface metadata.
    """

    power_voltage_v: float = 12.0
    power_connector: str = "XT30 / JST-XH"
    data_protocol: str = "MAVLink / IP Ethernet"
    required_bandwidth_mbps: float = 10.0
    metadata: dict[str, Any] = field(default_factory=dict)
