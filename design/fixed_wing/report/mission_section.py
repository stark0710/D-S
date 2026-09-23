"""
Fixed-Wing Mission Overview Section Compiler

Purpose:
    Defines the mission overview content generation.

Role in Architecture:
    `MissionSectionCompiler` reviews payload targets, operating altitudes, and energy requirements.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class MissionSectionCompiler:
    """
    Compiler for the Mission Overview chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        profile = requirements.mission_result.mission_profile
        constraints = requirements.mission_result.constraints

        content = (
            f"# Mission Overview\n\n"
            f"The UAV design is governed by the following operational constraints:\n"
            f"*   **Category**: {profile.mission_category.name}\n"
            f"*   **Target Payload**: {profile.payload_kg:.2f} kg\n"
            f"*   **Flight Time Limit**: {profile.flight_time_min:.1f} minutes\n"
            f"*   **Cruise Speed Target**: {profile.cruise_speed_kmh:.1f} km/h\n"
            f"*   **Stall Speed Boundary**: {constraints.maximum_stall_speed_kmh:.1f} km/h\n"
            f"*   **Launch & Recovery**: {profile.launch_method.name} launch and {profile.landing_method.name} recovery.\n"
        )
        return content
