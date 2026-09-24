"""
VTOL Fuselage Compartments Subsystem

Purpose:
    Defines the `Compartment` and `CompartmentLayout` classes partitioning
    internal spaces for payload, avionics, and power packs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class Compartment:
    """
    Allocated slot/volume for a specific subsystem.

    Attributes:
        name (str): Bay name.
        volume_m3 (float): Total allocated cubic volume.
        length_m (float): Bay length.
        width_m (float): Bay width.
        height_m (float): Bay height.
        position_x_m (float): Centroid location from nose in meters.
        is_accessible (bool): Sized hatch opening accessibility.
    """

    name: str
    volume_m3: float
    length_m: float
    width_m: float
    height_m: float
    position_x_m: float
    is_accessible: bool


@dataclass(slots=True)
class CompartmentLayout:
    """
    Fuselage internal structural partition layout.

    Attributes:
        battery_bay (Compartment): Sized battery compartment.
        payload_bay (Compartment): Sized payload compartment.
        avionics_bay (Compartment): Sized avionics compartment.
        metadata (Dict[str, Any]): Structural bulkheads placement.
    """

    battery_bay: Compartment
    payload_bay: Compartment
    avionics_bay: Compartment
    metadata: Dict[str, Any] = field(default_factory=dict)
