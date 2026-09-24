"""
Fixed-Wing Verification Subsystem Compliance Report Model

Purpose:
    Defines the `ComplianceReport` class.

Role in Architecture:
    `ComplianceReport` stores compliance percentages and checklist statuses.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass(slots=True)
class ComplianceReport:
    """
    Design compliance checklist audit report.

    Attributes:
        compliance_score_pct (float): compliance percentage (0.0 to 100.0).
        is_fully_compliant (bool): Flag indicating if compliance criteria are satisfied.
        verified_categories (List[str]): Passed sizing categories.
        failed_categories (List[str]): Failed sizing categories.
        compliance_details (Dict[str, str]): Details per category.
    """

    compliance_score_pct: float
    is_fully_compliant: bool
    verified_categories: List[str] = field(default_factory=list)
    failed_categories: List[str] = field(default_factory=list)
    compliance_details: Dict[str, str] = field(default_factory=dict)
