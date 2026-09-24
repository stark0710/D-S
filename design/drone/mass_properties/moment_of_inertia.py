"""
MomentOfInertia Subsystem

Purpose:
    Defines the `MomentOfInertia` domain model and Parallel Axis Theorem calculation service.

Role in Architecture:
    `MomentOfInertia` calculates 3D rotational moments of inertia (Ixx, Iyy, Izz in kg*m^2) around the CG axes.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.mass_properties.component_mass import ComponentMass
from backend.design.drone.mass_properties.center_of_gravity import CenterOfGravity


@dataclass(slots=True)
class MomentOfInertia:
    """
    Multirotor 3D Moment of Inertia (MoI) tensor model.

    Attributes:
        ixx_kg_m2 (float): Roll axis moment of inertia in kg*m^2.
        iyy_kg_m2 (float): Pitch axis moment of inertia in kg*m^2.
        izz_kg_m2 (float): Yaw axis moment of inertia in kg*m^2.
        ixy_kg_m2 (float): Off-diagonal product of inertia in kg*m^2.
        ixz_kg_m2 (float): Off-diagonal product of inertia in kg*m^2.
        iyz_kg_m2 (float): Off-diagonal product of inertia in kg*m^2.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    ixx_kg_m2: float
    iyy_kg_m2: float
    izz_kg_m2: float
    ixy_kg_m2: float = 0.0
    ixz_kg_m2: float = 0.0
    iyz_kg_m2: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class MomentOfInertiaCalculator:
    """
    Calculation service for 3D Moments of Inertia using the Parallel Axis Theorem.

    Design Principles:
        - Single Responsibility Principle: Rotational inertia tensor computation only.
    """

    def calculate_moi(self, components: list[ComponentMass], cg: CenterOfGravity) -> MomentOfInertia:
        """
        Calculates Ixx, Iyy, Izz relative to the CG axes:
        Ixx = sum(m_i * ((y_i - y_cg)^2 + (z_i - z_cg)^2)) / 1e6
        Iyy = sum(m_i * ((x_i - x_cg)^2 + (z_i - z_cg)^2)) / 1e6
        Izz = sum(m_i * ((x_i - x_cg)^2 + (y_i - y_cg)^2)) / 1e6

        Args:
            components (list[ComponentMass]): Component list with 3D positions.
            cg (CenterOfGravity): Aircraft 3D CG.

        Returns:
            MomentOfInertia: Computed inertia tensor model.
        """
        ixx_g_mm2 = 0.0
        iyy_g_mm2 = 0.0
        izz_g_mm2 = 0.0

        for c in components:
            dx = c.position_x_mm - cg.cg_x_mm
            dy = c.position_y_mm - cg.cg_y_mm
            dz = c.position_z_mm - cg.cg_z_mm

            ixx_g_mm2 += c.mass_g * ((dy ** 2) + (dz ** 2))
            iyy_g_mm2 += c.mass_g * ((dx ** 2) + (dz ** 2))
            izz_g_mm2 += c.mass_g * ((dx ** 2) + (dy ** 2))

        # Convert g*mm^2 to kg*m^2 (divide by 1e3 for kg, 1e6 for m^2 -> 1e9)
        ixx = ixx_g_mm2 / 1e9
        iyy = iyy_g_mm2 / 1e9
        izz = izz_g_mm2 / 1e9

        return MomentOfInertia(
            ixx_kg_m2=round(ixx, 4),
            iyy_kg_m2=round(iyy, 4),
            izz_kg_m2=round(izz, 4)
        )
