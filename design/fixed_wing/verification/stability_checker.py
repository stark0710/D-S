"""
Fixed-Wing Verification Stability Checker Subsystem

Purpose:
    Defines the `StabilityChecker` class.

Role in Architecture:
    `StabilityChecker` verifies static margin limits.
"""

from typing import List
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


class StabilityChecker:
    """
    Sizing audit for pitch, yaw, and roll static stability margins.
    """

    def check_stability_suitability(self, reqs: VerificationRequirements) -> List[str]:
        failures: List[str] = []
        mass_res = reqs.mass_result

        # Static margin checks
        if mass_res.static_margin < 0.05:
            failures.append(
                f"Dangerous stability margin ({mass_res.static_margin*100:.1f}%). "
                "The aircraft is unstable or neutrally stable in pitch. High risk of loss of control."
            )
        elif mass_res.static_margin > 0.25:
            failures.append(
                f"Excessive static stability margin ({mass_res.static_margin*100:.1f}%). "
                "The aircraft is excessively nose-heavy, causing high trim drag and limited elevator pitch control authority."
            )

        return failures
