"""
Fixed-Wing Mission Verification Result Subsystem

Purpose:
    Defines the `VerificationResult` class representing the consolidated checklist and compliance reports.

Role in Architecture:
    `VerificationResult` carries risk levels, checklists, violations, and corrective design advice.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from backend.design.fixed_wing.verification.compliance_report import ComplianceReport
from backend.design.fixed_wing.verification.risk_analysis import RiskAnalysis


@dataclass(slots=True)
class VerificationResult:
    """
    Consolidated output of the design compliance and safety verification process.

    Attributes:
        mission_status (str): Suitability of the aircraft for target operations (e.g. Ready, Deficient).
        verification_status (str): Sizing status matching bounds (e.g. Verified, Failed).
        requirement_results (Dict[str, bool]): Map of parsed items to their passing flags.
        compliance_report (ComplianceReport): Sized compliance details.
        risk_analysis (RiskAnalysis): risk assessment index.
        constraint_violations (List[str]): List of active constraint violations.
        engineering_notes (List[str]): Sizing rationale notes.
        recommendations (List[str]): flight operation guidelines.
        corrective_actions (List[str]): Recommended design changes if compliance fails.
        warnings (List[str]): List of warnings.
        metadata (Dict[str, Any]): Timestamps, version numbers, etc.
    """

    mission_status: str
    verification_status: str
    requirement_results: Dict[str, bool]
    compliance_report: ComplianceReport
    risk_analysis: RiskAnalysis
    constraint_violations: List[str] = field(default_factory=list)
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    corrective_actions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
"""
Fixed-Wing Verification Result model.
"""
