"""
Fixed-Wing Moments of Inertia Calculator Subsystem

Purpose:
    Defines the `InertiaCalculator` class.

Role in Architecture:
    `InertiaCalculator` calculates principal rolling, pitching, and yawing moments of inertia
    relative to the aircraft's center of gravity.
"""

from typing import List, Tuple
from backend.design.fixed_wing.mass_properties.component_mass import ComponentMass


class InertiaCalculator:
    """
    Service class executing parallel axis theorem point-mass inertia approximations.
    """

    def calculate_moments_of_inertia(
        self, components: List[ComponentMass], cg_x: float, cg_y: float, cg_z: float
    ) -> Tuple[float, float, float]:
        """
        Computes rolling (Ixx), pitching (Iyy), and yawing (Izz) moments in kg*m^2.
        """
        ixx = 0.0
        iyy = 0.0
        izz = 0.0

        for c in components:
            # Shift coordinates relative to the centered CG
            dx = c.x_m - cg_x
            dy = c.y_m - cg_y
            dz = c.z_m - cg_z

            # point mass approximations: I = m * r^2
            ixx += c.mass_kg * (dy**2 + dz**2)
            iyy += c.mass_kg * (dx**2 + dz**2)
            izz += c.mass_kg * (dx**2 + dy**2)

        return ixx, iyy, izz
