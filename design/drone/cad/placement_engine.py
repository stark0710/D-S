"""
PlacementEngine Subsystem

Purpose:
    Defines the `PlacementEngine` class for computing 3D spatial transformation matrices and mounting coordinates.

Role in Architecture:
    `PlacementEngine` positions components relative to the frame origin coordinate system based on arm layout and CG balance requirements.
"""

from backend.design.drone.cad.cad_component import CADComponent


class PlacementEngine:
    """
    Component 3D placement and reference coordinate system engine.

    Design Principles:
        - Single Responsibility Principle: 3D spatial translation and rotation coordinate computation only.
    """

    def apply_placement(
        self,
        component: CADComponent,
        position_mm: tuple[float, float, float],
        rotation_deg: tuple[float, float, float] = (0.0, 0.0, 0.0)
    ) -> CADComponent:
        """
        Applies 3D translation and rotation coordinates to a CAD component.

        Args:
            component (CADComponent): Target component.
            position_mm (tuple[float, float, float]): (X, Y, Z) in mm.
            rotation_deg (tuple[float, float, float]): (Roll, Pitch, Yaw) in deg.

        Returns:
            CADComponent: Updated component with position and rotation.
        """
        component.position_mm = position_mm
        component.rotation_deg = rotation_deg
        return component
