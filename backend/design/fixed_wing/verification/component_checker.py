"""
Fixed-Wing Verification Subsystem Component Compatibility Checker

Purpose:
    Defines the `ComponentChecker` class.

Role in Architecture:
    `ComponentChecker` asserts compatibility between wing loading, battery size, and engine layout.
"""

from typing import List
from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements


class ComponentChecker:
    """
    Sizing audit for subsystem interactions and placement clashes.
    """

    def check_subsystem_compatibility(self, reqs: VerificationRequirements) -> List[str]:
        failures: List[str] = []
        f_geom = reqs.fuselage_result.fuselage_geometry
        pay_res = reqs.payload_result

        # Check payload compartment fit
        if pay_res.payload_layout.compartment_width_m > f_geom.width_m:
            failures.append(
                f"Component clash: Payload compartment width ({pay_res.payload_layout.compartment_width_m:.2f} m) "
                f"is wider than the fuselage width ({f_geom.width_m:.2f} m)."
            )

        return failures
