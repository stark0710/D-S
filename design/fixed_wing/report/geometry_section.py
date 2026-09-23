"""
Fixed-Wing Geometry Sizing Section Compiler

Purpose:
    Defines the geometry characteristics content generation.

Role in Architecture:
    `GeometrySectionCompiler` compiles wingspan, tail spans, and fuselage envelopes.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class GeometrySectionCompiler:
    """
    Compiler for the Geometry chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        wing = requirements.wing_result.wing_geometry
        fuse = requirements.fuselage_result.fuselage_geometry
        tail = requirements.tail_result

        content = (
            f"# Geometry Sizing\n\n"
            f"### Wing Dimensions\n"
            f"*   **Wingspan**: {wing.span_m:.2f} m\n"
            f"*   **Root Chord**: {wing.root_chord_m:.2f} m\n"
            f"*   **Tip Chord**: {wing.tip_chord_m:.2f} m\n"
            f"*   **Reference Area**: {wing.reference_area_m2:.2f} m^2\n"
            f"*   **Aspect Ratio**: {wing.aspect_ratio:.1f}\n"
            f"*   **Dihedral**: {wing.dihedral_angle_deg:.1f} deg\n\n"
            
            f"### Fuselage Outer Envelope\n"
            f"*   **Total Length**: {fuse.length_m:.2f} m\n"
            f"*   **Maximum Width**: {fuse.width_m:.2f} m\n"
            f"*   **Maximum Height**: {fuse.height_m:.2f} m\n\n"
            
            f"### Tail Stabilizers\n"
            f"*   **Configuration**: {tail.tail_configuration}\n"
            f"*   **Horizontal stabilizer span**: {tail.horizontal_tail.span_m:.2f} m\n"
            f"*   **Vertical fin height**: {tail.vertical_tail.height_m:.2f} m\n"
        )
        return content
