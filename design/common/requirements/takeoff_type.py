"""
TakeoffType Enumeration Subsystem

Purpose:
    Defines the `TakeoffType` enumeration representing aircraft takeoff operational modes.

Role in Architecture:
    `TakeoffType` specifies how the aircraft transitions from ground to flight (Vertical, Runway, Catapult, Hand Launch).
    It acts as a key constraint in vehicle category suitability evaluation and structural design.
"""

from enum import Enum


class TakeoffType(str, Enum):
    """
    Takeoff method classification.

    Members:
        VERTICAL: Vertical hover takeoff (multirotors, VTOLs, helicopters).
        RUNWAY: Conventional ground roll takeoff on prepared/unprepared runways.
        CATAPULT: Pneumatic or bungee catapult launch for fixed-wing UAVs.
        HAND_LAUNCH: Manual hand throw launch for small fixed-wing UAVs.
    """
    VERTICAL = "VERTICAL"
    RUNWAY = "RUNWAY"
    CATAPULT = "CATAPULT"
    HAND_LAUNCH = "HAND_LAUNCH"
