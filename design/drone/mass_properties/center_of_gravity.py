"""
CenterOfGravity Subsystem

Purpose:
    Defines the `CenterOfGravity` domain model and 3D CG calculation service.

Role in Architecture:
    `CenterOfGravity` calculates 3D Center of Gravity coordinates (\bar{X}, \bar{Y}, \bar{Z} in mm) relative to origin.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mass_properties.component_mass import ComponentMass


@dataclass(slots=True)
class CenterOfGravity:
    """
    Multirotor Center of Gravity (CG) 3D coordinate model.

    Attributes:
        cg_x_mm (float): Longitudinal CG coordinate in mm.
        cg_y_mm (float): Lateral CG coordinate in mm.
        cg_z_mm (float): Vertical CG coordinate in mm.
        cg_margin_x_mm (float): Allowable longitudinal CG displacement limit in mm.
        cg_margin_y_mm (float): Allowable lateral CG displacement limit in mm.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    cg_x_mm: float
    cg_y_mm: float
    cg_z_mm: float
    cg_margin_x_mm: float = 15.0
    cg_margin_y_mm: float = 15.0
    metadata: dict[str, Any] = field(default_factory=dict)


class CenterOfGravityCalculator:
    """
    Calculation service for 3D Center of Gravity coordinates.

    Design Principles:
        - Single Responsibility Principle: Weighted 3D center of gravity spatial moment calculation only.
    """

    def calculate_cg(self, components: list[ComponentMass]) -> CenterOfGravity:
        """
        Calculates 3D CG coordinates: X_cg = sum(m_i * x_i) / sum(m_i).

        Args:
            components (list[ComponentMass]): List of component masses with 3D positions.

        Returns:
            CenterOfGravity: Computed 3D CG model.
        """
        total_m = sum(c.mass_g for c in components)
        if total_m <= 0:
            return CenterOfGravity(0.0, 0.0, 0.0)

        sum_mx = sum(c.mass_g * c.position_x_mm for c in components)
        sum_my = sum(c.mass_g * c.position_y_mm for c in components)
        sum_mz = sum(c.mass_g * c.position_z_mm for c in components)

        cg_x = sum_mx / total_m
        cg_y = sum_my / total_m
        cg_z = sum_mz / total_m

        return CenterOfGravity(
            cg_x_mm=round(cg_x, 2),
            cg_y_mm=round(cg_y, 2),
            cg_z_mm=round(cg_z, 2),
            cg_margin_x_mm=15.0,
            cg_margin_y_mm=15.0
        )
