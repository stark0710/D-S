"""
VehicleFamily Enumeration Subsystem

Purpose:
    Defines the canonical `VehicleFamily` enumeration representing the 3 primary aircraft families.

Role in Architecture:
    `VehicleFamily` is the sole valid public aircraft-family output of the Vehicle Selection Engine.
"""

from enum import Enum


class VehicleFamily(str, Enum):
    """
    Canonical top-level aircraft family classification.

    Members:
        FIXED_WING: Conventional, flying-wing, or catapult/runway wing-borne UAV family.
        MULTIROTOR: Quadcopter, hexacopter, octocopter, or multi-rotor hover UAV family.
        VTOL: Vertical Take-Off and Landing hybrid aircraft family.
    """
    FIXED_WING = "FIXED_WING"
    MULTIROTOR = "MULTIROTOR"
    VTOL = "VTOL"
