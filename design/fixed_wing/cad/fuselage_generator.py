"""
Fixed-Wing CAD Fuselage Generator Subsystem

Purpose:
    Defines the `FuselageGenerator` class.

Role in Architecture:
    `FuselageGenerator` generates the fuselage shell.
"""

from backend.design.fixed_wing.cad.part_generator import PartGenerator


class FuselageGenerator(PartGenerator):
    """
    Parametric fuselage pod generator.
    """

    def generate_fuselage(
        self,
        length_m: float,
        width_m: float,
        height_m: float,
    ) -> str:
        """
        Generates fuselage outer envelope.

        Returns:
            str: Solid representation string.
        """
        fuse_shell = self.builder.create_box("FuselageShell", length_m, width_m, height_m)
        # Apply fillet on edges
        fuse_solid = self.builder.fillet_edges(fuse_shell, 0.05)
        self.tree.add_feature("FilletBox", "fuselage", {"length": length_m, "width": width_m, "height": height_m})
        return fuse_solid
