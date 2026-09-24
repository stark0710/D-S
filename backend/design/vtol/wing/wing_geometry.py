"""
VTOL Wing Geometry Subsystem

Purpose:
    Defines the `WingGeometry` class representing sized parameters.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class WingGeometry:
    """
    Sized geometry parameters for a VTOL wing.

    Attributes:
        wing_type (str): Type of wing configuration (e.g. High Wing, Box Wing).
        span_m (float): Total wingspan in meters.
        area_m2 (float): Wing planform area in square meters.
        aspect_ratio (float): Wing aspect ratio.
        sweep_deg (float): Leading-edge sweep angle in degrees.
        dihedral_deg (float): Wing dihedral angle in degrees.
        anhedral_deg (float): Wing anhedral angle in degrees.
        incidence_deg (float): Mounting angle of incidence in degrees.
        washout_deg (float): Twist/washout angle in degrees.
        taper_ratio (float): Tip-to-root chord taper ratio.
        root_chord_m (float): Chord length at centerline/root.
        tip_chord_m (float): Chord length at tip.
        wing_position (str): Placement height on fuselage (e.g. High, Mid, Low).
        metadata (Dict[str, Any]): Intermediate geometry dimensions.
    """

    wing_type: str
    span_m: float
    area_m2: float
    aspect_ratio: float
    sweep_deg: float
    dihedral_deg: float
    anhedral_deg: float
    incidence_deg: float
    washout_deg: float
    taper_ratio: float
    root_chord_m: float
    tip_chord_m: float
    wing_position: str
    metadata: Dict[str, Any] = field(default_factory=dict)
