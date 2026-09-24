"""
VTOL Fuselage Internal Packaging Subsystem

Purpose:
    Defines the `SubsystemPlacement` and `InternalLayout` classes tracking
    internal component locations and sizing their CG effects.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class SubsystemPlacement:
    """
    Position and properties of an internal subsystem.

    Attributes:
        name (str): The subsystem identifier (e.g. Battery pack, Payload gimbal).
        x_m (float): Longitudinal offset from CG.
        y_m (float): Lateral offset from centerline.
        z_m (float): Vertical offset from centerline.
        mass_kg (float): Subsystem mass in kg.
        volume_m3 (float): Subsystem volume packaging requirement.
    """

    name: str
    x_m: float
    y_m: float
    z_m: float
    mass_kg: float
    volume_m3: float


@dataclass(slots=True)
class InternalLayout:
    """
    Consolidated packaging positions of all internal subsystems.

    Attributes:
        placements (List[SubsystemPlacement]): placements list.
        packaging_efficiency (float): Sized packaging volume utility ratio.
        center_of_gravity_x_m (float): Sized aircraft center-of-gravity.
        metadata (Dict[str, Any]): Intermediate CG balances.
    """

    placements: List[SubsystemPlacement]
    packaging_efficiency: float
    center_of_gravity_x_m: float
    metadata: Dict[str, Any] = field(default_factory=dict)
