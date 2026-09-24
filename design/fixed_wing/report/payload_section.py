"""
Fixed-Wing Payload Section Compiler

Purpose:
    Defines the payload integration content generation.

Role in Architecture:
    `PayloadSectionCompiler` writes sensors configurations and compartments dimensions.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class PayloadSectionCompiler:
    """
    Compiler for the Payload chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        pay = requirements.payload_result

        content = (
            f"# Payload Subsystem Integration\n\n"
            f"The sized cargo and sensor configurations include:\n"
            f"*   **Selected Sensor**: {', '.join(pay.selected_payloads)}\n"
            f"*   **Compartment Volume**: {pay.payload_layout.compartment_length_m * 1000.0:.0f}mm x {pay.payload_layout.compartment_width_m * 1000.0:.0f}mm x {pay.payload_layout.compartment_height_m * 1000.0:.0f}mm\n"
            f"*   **Orientation & Hatch**: {pay.payload_layout.orientation} orientation via {pay.payload_layout.accessibility_description}.\n"
            f"*   **Mount Type**: {pay.payload_mounts[0].mount_style} with vibration damping via {pay.payload_mounts[0].vibration_isolation_type}.\n"
        )
        return content
