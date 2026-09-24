"""
Fixed-Wing Verification Performance Checker Subsystem

Purpose:
    Defines the `PerformanceChecker` class.

Role in Architecture:
    `PerformanceChecker` verifies rate of climb and takeoff distances.
"""

from typing import List
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


class PerformanceChecker:
    """
    Sizing audit for climb and takeoff roll constraints.
    """

    def check_performance_suitability(self, reqs: VerificationRequirements) -> List[str]:
        failures: List[str] = []
        f_perf = reqs.flight_result

        # Rate of climb check
        if f_perf.climb_analysis.rate_of_climb_m_s < 1.0:
            failures.append(
                f"Rate of climb is insufficient ({f_perf.climb_analysis.rate_of_climb_m_s:.2f} m/s). "
                "Danger of failing to clear obstacle lines."
            )

        # Takeoff distance check
        if f_perf.takeoff_analysis.takeoff_distance_m > 100.0:
            failures.append(
                f"Takeoff roll exceeds standard field limits ({f_perf.takeoff_analysis.takeoff_distance_m:.1f} m)."
            )

        return failures
