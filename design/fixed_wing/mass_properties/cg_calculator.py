"""
Fixed-Wing Center of Gravity Calculator Subsystem

Purpose:
    Defines the `CGCalculator` class.

Role in Architecture:
    `CGCalculator` sums mass moments to determine longitudinal, lateral, and vertical coordinates.
"""

from typing import List, Tuple
from backend.design.fixed_wing.mass_properties.component_mass import ComponentMass


class CGCalculator:
    """
    Service class solving three-dimensional center of gravity equations.
    """

    def calculate_cg(self, components: List[ComponentMass]) -> Tuple[float, float, float]:
        """
        Calculates center of gravity (X, Y, Z) in meters from nose/centerlines.
        """
        total_mass = sum(c.mass_kg for c in components)
        if total_mass <= 0.0:
            return 0.0, 0.0, 0.0

        sum_mx = sum(c.mass_kg * c.x_m for c in components)
        sum_my = sum(c.mass_kg * c.y_m for c in components)
        sum_mz = sum(c.mass_kg * c.z_m for c in components)

        return sum_mx / total_mass, sum_my / total_mass, sum_mz / total_mass
