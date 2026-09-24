"""
Fixed-Wing Payload Cooling Subsystem

Purpose:
    Defines the `PayloadCooling` class representing thermal venting specs.

Role in Architecture:
    `PayloadCooling` holds heat dissipation targets and intake/exhaust duct geometries.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PayloadCooling:
    """
    Thermal dissipation and venting configuration.

    Attributes:
        heat_dissipation_w (float): continuous heat dissipation target.
        cooling_type (str): Vent style (e.g. Passive heatsink, Forced convection scoop).
        required_intake_area_mm2 (float): Air scoop intake area.
        operating_temp_max_c (float): Maximum sensor safe operational temperature.
    """

    heat_dissipation_w: float
    cooling_type: str
    required_intake_area_mm2: float
    operating_temp_max_c: float
