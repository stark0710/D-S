"""
Fixed-Wing Mass Properties Section Compiler

Purpose:
    Defines the mass properties content generation.

Role in Architecture:
    `MassPropertiesSectionCompiler` reviews Center of Gravity offsets and moments of inertia.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class MassPropertiesSectionCompiler:
    """
    Compiler for the Mass Properties chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        mass = requirements.mass_result
        wb = mass.weight_breakdown

        content = (
            f"# Mass Properties & Weight Distribution\n\n"
            f"The aircraft weight breakdown is summarized below:\n"
            f"*   **Empty Structure weight**: {wb.structural_weight_kg:.2f} kg\n"
            f"*   **Battery weight**: {wb.battery_fuel_weight_kg:.2f} kg\n"
            f"*   **Useful Payload weight**: {wb.useful_load_kg:.2f} kg\n"
            f"*   **Takeoff Mass (MTOW)**: {wb.structural_weight_kg + wb.battery_fuel_weight_kg + wb.useful_load_kg:.2f} kg\n\n"
            f"### Center of Gravity & Inertia\n"
            f"*   **Center of Gravity (CG)**: X={mass.center_of_gravity[0]:.3f} m, Y={mass.center_of_gravity[1]:.3f} m, Z={mass.center_of_gravity[2]:.3f} m (relative to nose)\n"
            f"*   **Moments of Inertia**: Ixx={mass.moments_of_inertia[0]:.3f} kg*m^2, Iyy={mass.moments_of_inertia[1]:.3f} kg*m^2, Izz={mass.moments_of_inertia[2]:.3f} kg*m^2\n"
            f"*   **Static Pitch Stability Margin**: {mass.static_margin * 100.0:.1f}%\n"
        )
        return content
