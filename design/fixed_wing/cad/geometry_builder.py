"""
Fixed-Wing CAD Geometry Builder Subsystem

Purpose:
    Defines the `GeometryBuilder` class containing basic solid primitives and CAD operations.

Role in Architecture:
    `GeometryBuilder` translates feature calls into CAD solid body representations.
"""

from typing import Dict, Any, List


class GeometryBuilder:
    """
    Parametric geometry generator executing solid operations.
    """

    def __init__(self, backend_name: str) -> None:
        self.backend = backend_name

    def create_box(self, name: str, dx: float, dy: float, dz: float) -> str:
        """Returns solid representation of a box block."""
        return f"{self.backend}:Box({name}, dx={dx:.1f}, dy={dy:.1f}, dz={dz:.1f})"

    def create_cylinder(self, name: str, radius: float, height: float) -> str:
        """Returns solid representation of a cylinder cylinder."""
        return f"{self.backend}:Cylinder({name}, r={radius:.1f}, h={height:.1f})"

    def loft_profiles(self, name: str, sections_list: List[str]) -> str:
        """Returns solid representation of a loft between multiple 2D cross sections."""
        sections_str = ", ".join(sections_list)
        return f"{self.backend}:Loft({name}, sections=[{sections_str}])"

    def cut_solids(self, base_solid: str, tool_solid: str) -> str:
        """Applies boolean difference cut operation."""
        return f"{base_solid}-Cut({tool_solid})"

    def fillet_edges(self, base_solid: str, radius: float) -> str:
        """Applies filleting operation on solid edges."""
        return f"{base_solid}-Fillet(r={radius:.2f})"
