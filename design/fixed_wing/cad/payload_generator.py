"""
Fixed-Wing CAD Payload Generator Subsystem

Purpose:
    Defines the `PayloadGenerator` class.

Role in Architecture:
    `PayloadGenerator` generates camera mounts and cargo compartment blocks.
"""

from backend.design.fixed_wing.cad.part_generator import PartGenerator


class PayloadGenerator(PartGenerator):
    """
    Parametric camera bay and cargo container CAD shape generator.
    """

    def generate_payload(
        self,
        length_m: float,
        width_m: float,
        height_m: float,
    ) -> str:
        """
        Generates payload block shapes.

        Returns:
            str: Solid representation string.
        """
        pay_box = self.builder.create_box("PayloadCompartment", length_m, width_m, height_m)
        self.tree.add_feature("Box", "payload", {"length": length_m, "width": width_m, "height": height_m})
        return pay_box
