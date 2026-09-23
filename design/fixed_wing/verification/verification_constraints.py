"""
Fixed-Wing Verification Sizing Constraints Subsystem

Purpose:
    Defines the `VerificationConstraints` class to hold physical bounds.

Role in Architecture:
    `VerificationConstraints` collects passing score boundaries and risk envelopes.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class VerificationConstraints:
    """
    Sizing bounds restricting verification scores.

    Attributes:
        min_compliance_pct (float): Minimum overall design compliance rating (e.g. 85.0).
        max_acceptable_risk_rating (str): Allowed risk level ("Low", "Medium", "High").
        max_allowed_violations (int): Upper limit on allowable minor warnings.
    """

    min_compliance_pct: float = 85.0
    max_acceptable_risk_rating: str = "Medium"
    max_allowed_violations: int = 2
