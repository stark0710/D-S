"""
Fixed-Wing Verification Subsystem Constraint Violations Auditor

Purpose:
    Defines the `ConstraintChecker` class.

Role in Architecture:
    `ConstraintChecker` checks absolute geometric boundaries and counts violations.
"""

from typing import List
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


class ConstraintChecker:
    """
    Sizing audit for geometric constraints violations.
    """

    def check_constraints(self, reqs: VerificationRequirements) -> List[str]:
        failures: List[str] = []
        wing_geom = reqs.wing_result.wing_geometry

        # Check aspect ratio
        if wing_geom.aspect_ratio > 25.0:
            failures.append(
                f"Aspect ratio constraint violated: AR ({wing_geom.aspect_ratio:.1f}) is too high for structural stiffness."
            )

        return failures
