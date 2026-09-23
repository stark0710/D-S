"""
AircraftType Enumeration Subsystem

Purpose:
    Defines the `AircraftType` enumeration representing supported unmanned aircraft configuration categories.

Role in Architecture:
    `AircraftType` classifies the structural and aerodynamic category of candidate or selected aircraft.
    It is an optional requirement field in Engineering Advisor Mode (where the recommendation engine suggests it)
    and a mandatory selection in Manual Mode, used by `DesignEngineRouter` to dispatch design requests.
"""

from enum import Enum


class AircraftType(str, Enum):
    """
    Aircraft configuration category classification.

    Members:
        QUADCOPTER: 4-rotor multirotor drone.
        HEXACOPTER: 6-rotor multirotor drone.
        OCTOCOPTER: 8-rotor multirotor drone.
        FIXED_WING: Conventional, V-tail, or flying-wing UAV.
        VTOL: Vertical Take-Off and Landing hybrid aircraft.
        HELICOPTER: Single main rotor + tail rotor rotorcraft.
        HYBRID: Advanced multi-mode hybrid propulsion system.
    """
    QUADCOPTER = "QUADCOPTER"
    HEXACOPTER = "HEXACOPTER"
    OCTOCOPTER = "OCTOCOPTER"
    FIXED_WING = "FIXED_WING"
    VTOL = "VTOL"
    HELICOPTER = "HELICOPTER"
    HYBRID = "HYBRID"
