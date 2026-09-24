"""
VerificationResult Subsystem

Purpose:
    Defines the `VerificationResult` domain model representing output from the Drone Mission Verification Engineering Framework.

Role in Architecture:
    `VerificationResult` encapsulates overall status ('PASSED', 'MARGINAL', 'FAILED'), `VerificationScore`, `MissionComplianceResult`,
    `PerformanceVerificationResult`, `SafetyVerificationResult`, `ReliabilityVerificationResult`, `ConstraintVerificationResult`,
    passed requirements, failed requirements, engineering notes, recommendations, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.verification.verification_score import VerificationScore
from backend.design.drone.verification.mission_compliance import MissionComplianceResult
from backend.design.drone.verification.performance_verification import PerformanceVerificationResult
from backend.design.drone.verification.safety_verification import SafetyVerificationResult
from backend.design.drone.verification.reliability_verification import ReliabilityVerificationResult
from backend.design.drone.verification.constraint_verification import ConstraintVerificationResult


@dataclass(slots=True)
class VerificationResult:
    """
    Multirotor mission verification engineering output summary.

    Attributes:
        overall_status (str): Overall verification status ('PASSED', 'MARGINAL', 'FAILED').
        verification_score (VerificationScore): Composite verification confidence score model.
        mission_compliance (MissionComplianceResult): Mission requirements compliance model.
        performance_verification (PerformanceVerificationResult): Performance margins model.
        safety_verification (SafetyVerificationResult): Multi-discipline safety margins model.
        reliability_verification (ReliabilityVerificationResult): Subsystem redundancy and reliability model.
        constraint_verification (ConstraintVerificationResult): Engineering constraints compliance model.
        passed_requirements (list[str]): List of verified passed requirements.
        failed_requirements (list[str]): List of failed requirements.
        engineering_notes (str): Summary notes and technical rationale.
        recommendations (list[str]): Actionable engineering recommendations.
        warnings (list[str]): Diagnostic warnings generated during verification.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    overall_status: str
    verification_score: VerificationScore
    mission_compliance: MissionComplianceResult
    performance_verification: PerformanceVerificationResult
    safety_verification: SafetyVerificationResult
    reliability_verification: ReliabilityVerificationResult
    constraint_verification: ConstraintVerificationResult
    passed_requirements: list[str] = field(default_factory=list)
    failed_requirements: list[str] = field(default_factory=list)
    engineering_notes: str = ""
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
