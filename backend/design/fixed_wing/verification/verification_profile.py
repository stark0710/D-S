"""
Fixed-Wing Mission Verification Profile Subsystem

Purpose:
    Defines the `VerificationProfile` class.

Role in Architecture:
    The profile is used to configure risk safety thresholds and compliance limits.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class VerificationProfile:
    """
    Configuration profile defining limits and references for audit logs.

    Attributes:
        min_passing_compliance_pct (float): Minimum compliance score to pass audit (default 80.0 / 80%).
        max_acceptable_risk_score (float): Maximum risk score limit (default 40.0).
        warning_margin_coefficient (float): Reserve factor for checking margins (default 1.10).
    """

    min_passing_compliance_pct: float = 80.0
    max_acceptable_risk_score: float = 40.0
    warning_margin_coefficient: float = 1.10
