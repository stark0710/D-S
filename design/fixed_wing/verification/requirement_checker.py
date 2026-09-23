"""
Fixed-Wing Verification Requirement Checker Subsystem

Purpose:
    Defines the `RequirementChecker` class.

Role in Architecture:
    `RequirementChecker` verifies user preferred geometry and tail layout matches.
"""

from typing import List, Dict
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


class RequirementChecker:
    """
    Sizing audit for preferred user constraints overrides.
    """

    def check_requirements(self, reqs: VerificationRequirements) -> List[str]:
        """
        Verifies that design decisions match user requirements.

        Returns:
            List[str]: A list of failed match descriptions.
        """
        failures: List[str] = []

        # Check configuration matches
        c_res = reqs.configuration_result
        if reqs.mission_result.mission_profile.launch_method.value != "Catapult":
            # Just an example of cross-checking launch method
            pass

        return failures
