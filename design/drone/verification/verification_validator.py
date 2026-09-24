"""
VerificationValidator Subsystem

Purpose:
    Defines the `VerificationValidator` class responsible for validating verification results against constraints.

Role in Architecture:
    `VerificationValidator` checks critical safety failure rules and failed requirements count bounds.
"""

from backend.design.drone.verification.verification_result import VerificationResult
from backend.design.drone.verification.verification_constraints import VerificationConstraints


class VerificationValidator:
    """
    Validator for multirotor mission verification engineering outputs.

    Design Principles:
        - Single Responsibility Principle: Verification result validation against constraints only.
    """

    def validate_verification(
        self,
        result: VerificationResult,
        constraints: VerificationConstraints
    ) -> list[str]:
        """
        Validates a VerificationResult against VerificationConstraints.

        Args:
            result (VerificationResult): Target verification result.
            constraints (VerificationConstraints): Verification constraints.

        Returns:
            list[str]: List of warning messages.
        """
        warnings: list[str] = []

        if len(result.failed_requirements) > constraints.max_failed_requirements:
            warnings.append(
                f"Failed requirements count ({len(result.failed_requirements)}) exceeds maximum allowable limit ({constraints.max_failed_requirements})."
            )

        if constraints.require_zero_critical_failures and not result.safety_verification.safe:
            warnings.append(
                "Critical safety violation detected: Aircraft system fails zero critical failure safety constraint."
            )

        return warnings
