"""
Fixed-Wing Verification Validator Subsystem

Purpose:
    Defines the `VerificationValidator` class to validate compliance scores and risk indices.

Role in Architecture:
    `VerificationValidator` blocks design handoff if compliance scores are below passing thresholds.
"""

from typing import List


class VerificationValidationError(ValueError):
    """Exception raised when sized verification results fail safety thresholds."""
    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


class VerificationValidator:
    """
    Validator enforcing design safety and compliance boundaries.
    """

    def validate(
        self,
        compliance_pct: float,
        min_compliance_pct: float,
        risk_score: float,
        max_risk_score: float,
        violations: List[str],
    ) -> List[str]:
        """
        Validates the sized verification metrics.

        Returns:
            List[str]: A list of non-fatal warnings (compromises).

        Raises:
            VerificationValidationError: If critical constraints are violated.
        """
        errors: List[str] = []
        warnings: List[str] = []

        if compliance_pct < min_compliance_pct:
            errors.append(
                f"Design compliance score ({compliance_pct:.1f}%) is below the "
                f"minimum required safety compliance boundary ({min_compliance_pct:.1f}%)."
            )

        if risk_score > max_risk_score:
            errors.append(
                f"Calculated aircraft design risk index ({risk_score:.1f}) exceeds the "
                f"maximum acceptable safety threshold ({max_risk_score:.1f})."
            )

        if len(violations) > 3:
            errors.append(
                f"Excessive active constraint violations detected ({len(violations)}). "
                "Design requires immediate structural modifications."
            )

        if errors:
            raise VerificationValidationError(errors)

        return warnings
