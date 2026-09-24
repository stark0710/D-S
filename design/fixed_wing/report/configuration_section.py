"""
Fixed-Wing Configuration Section Compiler

Purpose:
    Defines the configuration choice content generation.

Role in Architecture:
    `ConfigurationSectionCompiler` writes summaries of selected layout configurations.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class ConfigurationSectionCompiler:
    """
    Compiler for the Configuration chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        layout = requirements.configuration_result

        content = (
            f"# Configuration Layout\n\n"
            f"The layout selection process identified the following optimal structural configuration:\n"
            f"*   **Wing Placement**: {layout.wing_configuration}\n"
            f"*   **Propulsion Layout**: {layout.propulsion_configuration}\n"
            f"*   **Tail Assembly**: {layout.tail_configuration}\n"
            f"*   **Landing Gear**: {layout.landing_gear_configuration}\n\n"
            f"**Engineering Rationale**:\n"
            f"{layout.engineering_rationale}\n"
        )
        return content
