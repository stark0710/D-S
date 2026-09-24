"""
Fixed-Wing Avionics Section Compiler

Purpose:
    Defines the avionics content generation.

Role in Architecture:
    `AvionicsSectionCompiler` lists the autopilot flight controller and communication link budgets.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class AvionicsSectionCompiler:
    """
    Compiler for the Avionics chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        av = requirements.avionics_result

        content = (
            f"# Onboard Avionics Systems\n\n"
            f"The flight control configuration consists of the following modules:\n"
            f"*   **Flight Controller Hardware**: {av.selected_flight_controller} (firmware: {av.selected_firmware})\n"
            f"*   **GPS/GNSS Module**: {av.selected_navigation_system}\n"
            f"*   **RC Control Receiver**: {av.selected_receiver}\n"
            f"*   **Telemetry Data Link**: {av.selected_telemetry}\n"
            f"*   **Continuous power BEC draw**: {av.power_analysis.continuous_power_w:.1f} W\n"
        )
        return content
