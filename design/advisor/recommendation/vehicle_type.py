"""
VehicleType Enumeration Subsystem

Purpose:
    Defines the `VehicleType` enumeration representing aircraft categories evaluated by the Recommendation Platform.

Role in Architecture:
    `VehicleType` classifies candidate vehicle configurations evaluated during category recommendation.
"""

from enum import Enum


class VehicleType(str, Enum):
    """
    Candidate aircraft category classification.

    Members:
        QUADCOPTER: 4-rotor multirotor drone.
        HEXACOPTER: 6-rotor multirotor drone.
        OCTOCOPTER: 8-rotor multirotor drone.
        FIXED_WING: Conventional or flying-wing UAV.
        VTOL: Vertical Take-Off and Landing hybrid aircraft.
    """
    QUADCOPTER = "QUADCOPTER"
    HEXACOPTER = "HEXACOPTER"
    OCTOCOPTER = "OCTOCOPTER"
    FIXED_WING = "FIXED_WING"
    VTOL = "VTOL"
