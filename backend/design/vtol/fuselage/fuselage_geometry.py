"""
VTOL Fuselage Geometry Subsystem

Purpose:
    Defines the `FuselageGeometry` class storing external dimensions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class FuselageGeometry:
    """
    Planform geometry parameters of the sized fuselage.

    Attributes:
        fuselage_type (str): Sized fuselage configuration type.
        length_m (float): Sized length.
        width_m (float): Sized width.
        height_m (float): Sized height.
        cross_section_shape (str): Shape profile (e.g. Oval, Rectangular).
        volume_m3 (float): Sized total volume capacity.
        wetted_area_m2 (float): Fuselage skin wetted surface area.
        frontal_area_m2 (float): Frontal project area driving drag.
        metadata (Dict[str, Any]): Additional cross-sectional ratios.
    """

    fuselage_type: str
    length_m: float
    width_m: float
    height_m: float
    cross_section_shape: str
    volume_m3: float
    wetted_area_m2: float
    frontal_area_m2: float
    metadata: Dict[str, Any] = field(default_factory=dict)
