"""
Fixed-Wing CAD Fastener Generator Subsystem

Purpose:
    Defines the `FastenerGenerator` class.

Role in Architecture:
    `FastenerGenerator` generates bolts, sleeves, holes, and joints.
"""

from backend.design.fixed_wing.cad.part_generator import PartGenerator


class FastenerGenerator(PartGenerator):
    """
    Parametric fastener, bolt hole, and spar joint sleeve generator.
    """

    def generate_bolt(
        self,
        name: str,
        bolt_diameter_mm: float,
        bolt_length_mm: float,
    ) -> str:
        """
        Generates bolt geometries.

        Returns:
            str: Solid representation string.
        """
        bolt = self.builder.create_cylinder(name, bolt_diameter_mm / 2000.0, bolt_length_mm / 1000.0)
        self.tree.add_feature("BoltCylinder", name, {"diameter_mm": bolt_diameter_mm, "length_mm": bolt_length_mm})
        return bolt
