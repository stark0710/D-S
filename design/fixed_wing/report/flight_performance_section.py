"""
Fixed-Wing Flight Performance Section Compiler

Purpose:
    Defines the flight performance content generation.

Role in Architecture:
    `FlightPerformanceSectionCompiler` reviews takeoff rolls, cruise ranges, and absolute ceilings.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class FlightPerformanceSectionCompiler:
    """
    Compiler for the Flight Performance chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        flight = requirements.flight_result

        content = (
            f"# Flight Performance\n\n"
            f"Aerodynamic flight envelope parameters are detailed below:\n"
            f"*   **Takeoff ground roll**: {flight.takeoff_analysis.takeoff_distance_m:.1f} meters\n"
            f"*   **Stall Speed**: {flight.stall_analysis.stall_speed_clean_kmh:.1f} km/h (landing configuration: {flight.stall_analysis.stall_speed_landing_kmh:.1f} km/h)\n"
            f"*   **Rate of Climb (ROC)**: {flight.climb_analysis.rate_of_climb_m_s:.1f} m/s\n"
            f"*   **Max Range**: {flight.range_analysis.maximum_range_km:.1f} km\n"
            f"*   **Max Endurance**: {flight.endurance_analysis.maximum_endurance_min:.1f} minutes\n"
            f"*   **Service Ceiling**: {flight.ceiling_analysis.service_ceiling_m:.0f} meters\n"
            f"*   **Maximum Turn G-Load**: {flight.turn_analysis.load_factor:.2f} G\n"
        )
        return content
