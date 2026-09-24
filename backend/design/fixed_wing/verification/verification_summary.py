"""
Fixed-Wing Verification Subsystem Summary Report Model

Purpose:
    Defines the `VerificationSummary` class.

Role in Architecture:
    `VerificationSummary` compiles passing statuses and sizing coverage scores.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class VerificationSummary:
    """
    Consolidated brief of design check results.

    Attributes:
        summary_text (str): Sizing checklist description.
        status (str): Overall check status ("Verified", "Deficient").
        total_requirements (int): Count of audited items.
        passed_requirements (int): Count of successfully passed items.
    """

    summary_text: str
    status: str
    total_requirements: int
    passed_requirements: int
