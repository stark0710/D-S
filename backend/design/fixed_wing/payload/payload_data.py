"""
Fixed-Wing Payload Data Subsystem

Purpose:
    Defines the `PayloadDataInterface` class representing telecommunication link wires and bandwidth.

Role in Architecture:
    `PayloadDataInterface` holds bandwidth metrics and pins configs (Ethernet, Serial, USB).
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PayloadDataInterface:
    """
    Data communication interface.

    Attributes:
        interface_type (str): Hardware link (e.g. Ethernet RJ45, USB 3.0, UART).
        bandwidth_mbps (float): Data rate requirement.
        geotagging_protocol (str): Shutter synch method (e.g. Mavlink camera trigger, PWM feedback).
        datalogger_storage_gb (float): Sized local SD card storage requirements.
    """

    interface_type: str
    bandwidth_mbps: float
    geotagging_protocol: str
    datalogger_storage_gb: float
