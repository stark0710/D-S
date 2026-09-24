"""
OperatingEnvironment Enumeration Subsystem

Purpose:
    Defines the `OperatingEnvironment` enumeration representing environmental and terrain conditions.

Role in Architecture:
    `OperatingEnvironment` specifies atmospheric and terrain challenges (Urban, Rural, Mountain, Forest, Desert, Coastal, Marine, Indoor).
    It is used by Mission Analysis Engine and Rule Engine to evaluate environmental safety constraints.
"""

from enum import Enum


class OperatingEnvironment(str, Enum):
    """
    Environmental and terrain classification.

    Members:
        URBAN: High obstacle density, RF interference, and strict safety clearance requirements.
        RURAL: Open fields, agricultural land, and moderate environmental hazards.
        MOUNTAIN: High altitude, low air density, severe wind gusts, and thermal turbulence.
        FOREST: Canopy obstacles, constrained landing zones, and GPS degradation risks.
        DESERT: Extreme temperatures, high thermal currents, and airborne dust/sand.
        COASTAL: High wind speeds, salt fog exposure, and variable humidity.
        MARINE: Shipboard deployment, saltwater corrosion risks, and high wind turbulence.
        INDOOR: Enclosed spaces, zero GPS signal, and wall effect aerodynamic turbulence.
    """
    URBAN = "URBAN"
    RURAL = "RURAL"
    MOUNTAIN = "MOUNTAIN"
    FOREST = "FOREST"
    DESERT = "DESERT"
    COASTAL = "COASTAL"
    MARINE = "MARINE"
    INDOOR = "INDOOR"
