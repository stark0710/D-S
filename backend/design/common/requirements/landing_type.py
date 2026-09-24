"""
LandingType Enumeration Subsystem

Purpose:
    Defines the `LandingType` enumeration representing aircraft landing recovery operational modes.

Role in Architecture:
    `LandingType` specifies how the aircraft terminates flight and recovers to ground (Vertical, Runway, Parachute, Belly Landing, Net Recovery).
    It informs structural airframe sizing and operational complexity scoring.
"""

from enum import Enum


class LandingType(str, Enum):
    """
    Landing and recovery method classification.

    Members:
        VERTICAL: Precision vertical hover touchdown.
        RUNWAY: Conventional ground roll landing on landing gear.
        PARACHUTE: Emergency or standard ballistic parachute deployment recovery.
        BELLY_LANDING: Unpowered slide landing on reinforced airframe belly.
        NET_RECOVERY: Arrested recovery using ground net or wire capture.
    """
    VERTICAL = "VERTICAL"
    RUNWAY = "RUNWAY"
    PARACHUTE = "PARACHUTE"
    BELLY_LANDING = "BELLY_LANDING"
    NET_RECOVERY = "NET_RECOVERY"
