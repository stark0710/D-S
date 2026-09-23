"""
Fixed-Wing CAD Tail Generator Subsystem

Purpose:
    Defines the `TailGenerator` class.

Role in Architecture:
    `TailGenerator` generates horizontal and vertical fin stabilizers.
"""

from backend.design.fixed_wing.cad.part_generator import PartGenerator


class TailGenerator(PartGenerator):
    """
    Parametric tail fin and stabilizer model generator.
    """

    def generate_tail(
        self,
        tail_config: str,
        h_span: float,
        v_span: float,
    ) -> str:
        """
        Generates tail assembly shapes.

        Returns:
            str: Solid representation string.
        """
        h_fin = self.builder.create_box("HorizontalStabilizer", 0.15, h_span, 0.01)
        v_fin = self.builder.create_box("VerticalFin", 0.15, 0.01, v_span)
        
        tail_solid = f"TailAssembly({tail_config}, horizontal={h_fin}, vertical={v_fin})"
        self.tree.add_feature("AssemblyMerge", "tail", {"config": tail_config, "h_span": h_span, "v_span": v_span})
        return tail_solid
