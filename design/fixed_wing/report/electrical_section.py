"""
Fixed-Wing Electrical Section Compiler

Purpose:
    Defines the electrical system content generation.

Role in Architecture:
    `ElectricalSectionCompiler` reviews battery specs and wiring layouts.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class ElectricalSectionCompiler:
    """
    Compiler for the Electrical chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        # Electrical results map directly from requirements
        batt_weight = requirements.mass_result.weight_breakdown.battery_fuel_weight_kg

        content = (
            f"# Electrical & Power Distribution System\n\n"
            f"The onboard electrical power architecture is summarized below:\n"
            f"*   **Battery Pack Mass**: {batt_weight:.2f} kg\n"
            f"*   **Chemistry**: Lithium Polymer (LiPo)\n"
            f"*   **Specific Energy**: 200.0 Wh/kg\n"
            f"*   **Regulated Avionics Bus Voltage**: 5.0 V via continuous UBEC\n"
            f"*   **Power telemetry monitoring**: Sized airspeed & continuous BEC current links\n"
        )
        return content
