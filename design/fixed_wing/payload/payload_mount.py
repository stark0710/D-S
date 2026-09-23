"""
Fixed-Wing Payload Mount Subsystem

Purpose:
    Defines the `PayloadMount` class representing mounting styles and vibration isolation.

Role in Architecture:
    `PayloadMount` holds structural support specifications, isolator details, and gimbal degrees.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PayloadMount:
    """
    Mounting plate layout and shock absorption.

    Attributes:
        mount_style (str): Physical mount connection (e.g. 2-axis gimbal, Rigid floor plate).
        vibration_isolation_type (str): Dampers style (e.g. Alpha-gel rubber dampers).
        isolation_frequency_hz (float): Target vibration cutoff frequency.
        mounting_hardware (str): Fasteners (e.g. 4x M3 nylon screws).
        tilt_angle_limit_deg (float): Gimbal tilt limit in degrees.
    """

    mount_style: str
    vibration_isolation_type: str
    isolation_frequency_hz: float
    mounting_hardware: str
    tilt_angle_limit_deg: float
