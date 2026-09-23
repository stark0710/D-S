"""
Fixed-Wing Optimization Results Section Compiler

Purpose:
    Defines the optimization results content generation.

Role in Architecture:
    `OptimizationSectionCompiler` reviews sizing optimization passes (if available).
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class OptimizationSectionCompiler:
    """
    Compiler for the Optimization Results chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        opt = requirements.optimization_result

        if opt is None:
            content = (
                "# Optimization Results\n\n"
                "No optimization pass was executed for this design iteration. "
                "The aircraft was sized using direct analytical methods only.\n"
            )
        else:
            content = (
                "# Optimization Results\n\n"
                f"An optimization loop was executed. Summary:\n"
                f"*   **Optimization Data**: {opt}\n"
            )
        return content
