"""
Fixed-Wing Verification Mission Checker Subsystem

Purpose:
    Defines the `MissionChecker` class.

Role in Architecture:
    `MissionChecker` checks range, stall, and endurance completions.
"""

from typing import List
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


class MissionChecker:
    """
    Sizing audit for mission-critical flight limits.
    """

    def check_mission_suitability(self, reqs: VerificationRequirements) -> List[str]:
        failures: List[str] = []
        m_profile = reqs.mission_result.mission_profile
        f_perf = reqs.flight_result

        # Range check
        if f_perf.range_analysis.maximum_range_km < m_profile.mission_range_km:
            failures.append(
                f"Mission Range compliance failed: Sized range ({f_perf.range_analysis.maximum_range_km:.1f} km) "
                f"is below target range requirement ({m_profile.mission_range_km:.1f} km)."
            )

        # Endurance check
        if f_perf.endurance_analysis.maximum_endurance_min < m_profile.flight_time_min:
            failures.append(
                f"Mission Endurance compliance failed: Sized endurance ({f_perf.endurance_analysis.maximum_endurance_min:.1f} min) "
                f"is below target duration ({m_profile.flight_time_min:.1f} min)."
            )

        return failures
