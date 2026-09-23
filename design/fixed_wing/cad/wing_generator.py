"""
Fixed-Wing CAD Wing Generator Subsystem

Purpose:
    Defines the `WingGenerator` class.

Role in Architecture:
    `WingGenerator` generates parametric wings (lofting root to tip airfoils).
"""

from backend.design.fixed_wing.cad.part_generator import PartGenerator


class WingGenerator(PartGenerator):
    """
    Parametric wing model generator.
    """

    def generate_wing(
        self,
        span_m: float,
        root_chord_m: float,
        tip_chord_m: float,
        dihedral_deg: float,
        taper_ratio: float,
    ) -> str:
        """
        Generates wing solid body.

        Returns:
            str: Solid representation string.
        """
        # Define airfoil sections
        root_airfoil = f"AirfoilSection(root, chord={root_chord_m:.2f})"
        tip_airfoil = f"AirfoilSection(tip, chord={tip_chord_m:.2f}, y_offset={span_m/2.0:.2f}, z_offset={dihedral_deg:.1f})"
        
        wing_solid = self.builder.loft_profiles("WingMain", [root_airfoil, tip_airfoil])
        self.tree.add_feature("Loft", "wing", {"span": span_m, "dihedral": dihedral_deg, "taper": taper_ratio})
        return wing_solid
