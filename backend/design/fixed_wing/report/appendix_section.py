"""
Fixed-Wing Appendix Section Compiler

Purpose:
    Defines appendix content generation with mathematical derivations and references.

Role in Architecture:
    `AppendixSectionCompiler` writes supplementary reference formulas.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class AppendixSectionCompiler:
    """
    Compiler for the Appendices chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        wing = requirements.wing_result.wing_geometry

        content = (
            "# Appendices\n\n"
            "## A.1  Lift Equation Reference\n\n"
            "The lift force at stall is given by:\n"
            "    L = 0.5 × ρ × V² × S × CL_max\n\n"
            "Where:\n"
            "*   ρ = air density (kg/m³)\n"
            "*   V = airspeed (m/s)\n"
            "*   S = reference wing area (m²)\n"
            "*   CL_max = maximum lift coefficient\n\n"
            "## A.2  Drag Polar\n\n"
            "    CD = CD0 + K × CL²\n\n"
            "Where K = 1 / (π × AR × e) is the induced drag factor.\n\n"
            "## A.3  Design Parameters Summary\n\n"
            f"*   Wing Reference Area S = {wing.reference_area_m2:.3f} m²\n"
            f"*   Aspect Ratio AR = {wing.aspect_ratio:.1f}\n"
            f"*   Mean Aerodynamic Chord MAC = {wing.mean_aerodynamic_chord_m:.3f} m\n"
        )
        return content
