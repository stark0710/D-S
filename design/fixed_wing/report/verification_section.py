"""
Fixed-Wing Mission Verification Section Compiler

Purpose:
    Defines the verification status content generation.

Role in Architecture:
    `VerificationSectionCompiler` reviews compliance scoring and design deficiency risks.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class VerificationSectionCompiler:
    """
    Compiler for the Mission Verification chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        ver = requirements.verification_result

        content = (
            f"# Mission Verification & Compliance Checklist\n\n"
            f"The design was verified against required bounds:\n"
            f"*   **Compliance Score**: {ver.compliance_report.compliance_score_pct:.1f}%\n"
            f"*   **Qualitative Risk Level**: {ver.risk_analysis.risk_level}\n"
            f"*   **Risk Score**: {ver.risk_analysis.overall_risk_score:.1f}\n"
            f"*   **Verification Status**: {ver.verification_status}\n\n"
            f"### Active Warnings / Mitigations:\n"
        )
        for r in ver.warnings:
            content += f"*   [WARNING] {r}\n"
        if not ver.warnings:
            content += "*   No active verification warnings.\n"

        return content
