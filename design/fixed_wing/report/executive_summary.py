"""
Fixed-Wing Executive Summary Section Compiler

Purpose:
    Defines the executive summary content generation.

Role in Architecture:
    `ExecutiveSummaryCompiler` consolidates overall cost, flight range, and sizing status.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class ExecutiveSummaryCompiler:
    """
    Compiler for the Executive Summary chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        """Generates executive summary text."""
        profile = requirements.mission_result.mission_profile
        wing = requirements.wing_result.wing_geometry
        m_cost = requirements.manufacturing_result.manufacturing_cost

        summary = (
            f"# Executive Summary\n\n"
            f"This engineering document describes the parametric sizing and configuration results for the "
            f"Torq Wings fixed-wing UAV, optimized for '{profile.mission_category.name}' operations.\n\n"
            f"Key metrics for the proposed design:\n"
            f"*   **Wingspan**: {wing.span_m:.2f} meters\n"
            f"*   **Aspect Ratio**: {wing.aspect_ratio:.1f}\n"
            f"*   **Takeoff Mass**: {requirements.mass_result.weight_breakdown.battery_fuel_weight_kg + requirements.mass_result.weight_breakdown.structural_weight_kg:.2f} kg\n"
            f"*   **Production Cost Estimate**: {m_cost:.2f} USD\n"
            f"*   **Verification Rating**: {requirements.verification_result.compliance_report.compliance_score_pct:.1f}%\n"
            f"*   **Sizing Status**: {requirements.verification_result.verification_status}\n"
        )
        return summary
