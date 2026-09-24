"""
Fixed-Wing Verification Subsystem Risk Analysis Model

Purpose:
    Defines the `RiskAnalysis` dataclass representing engineering risk scores and failure modes.

Role in Architecture:
    `RiskAnalysis` holds the calculated risk indices and potential failure mitigations.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class RiskAnalysis:
    """
    Risk assessment parameters for the aircraft design.

    Attributes:
        overall_risk_score (float): Calculated risk index from 0.0 to 100.0.
        risk_level (str): Qualitative evaluation ("Low", "Medium", "High").
        identified_risks (List[str]): List of warning failure modes.
        mitigation_actions (List[str]): Actionable design steps to decrease risks.
    """

    overall_risk_score: float
    risk_level: str
    identified_risks: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)
