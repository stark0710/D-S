"""
Fixed-Wing CAD Assembly Builder Subsystem

Purpose:
    Defines the `AssemblyBuilder` class to compile hierarchical assemblies.

Role in Architecture:
    `AssemblyBuilder` translates part coordinates into placement transforms relative to the aircraft global origin.
"""

from typing import Dict, Any, List
from backend.design.fixed_wing.cad.coordinate_system import CoordinateSystem


class AssemblyBuilder:
    """
    Parametric assembly builder managing transforms.
    """

    def __init__(self) -> None:
        self.placements: List[Dict[str, Any]] = []

    def position_part(
        self,
        part_name: str,
        coord_sys: CoordinateSystem,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Positions a component solid relative to global frame coordinates.

        Returns:
            Dict[str, Any]: placement representation dictionary.
        """
        placement = {
            "component_name": part_name,
            "origin_x_m": coord_sys.origin[0],
            "origin_y_m": coord_sys.origin[1],
            "origin_z_m": coord_sys.origin[2],
            "roll_deg": coord_sys.orientation[0],
            "pitch_deg": coord_sys.orientation[1],
            "yaw_deg": coord_sys.orientation[2],
            "metadata": metadata if metadata else {},
        }
        self.placements.append(placement)
        return placement
