"""
Fixed-Wing Mission Verification Engineering Framework Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Mission Verification Framework.
"""

from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements
from backend.design.fixed_wing.verification.verification_profile import VerificationProfile
from backend.design.fixed_wing.verification.verification_constraints import VerificationConstraints
from backend.design.fixed_wing.verification.verification_result import VerificationResult
from backend.design.fixed_wing.verification.verification_validator import VerificationValidator, VerificationValidationError
from backend.design.fixed_wing.verification.compliance_report import ComplianceReport
from backend.design.fixed_wing.verification.risk_analysis import RiskAnalysis
from backend.design.fixed_wing.verification.verification_summary import VerificationSummary
from backend.design.fixed_wing.verification.verification_strategy import VerificationStrategy
from backend.design.fixed_wing.verification.verification_registry import VerificationStrategyRegistry
from backend.design.fixed_wing.verification.verification_engine import VerificationEngine

__all__ = [
    "VerificationRequirements",
    "VerificationProfile",
    "VerificationConstraints",
    "VerificationResult",
    "VerificationValidator",
    "VerificationValidationError",
    "ComplianceReport",
    "RiskAnalysis",
    "VerificationSummary",
    "VerificationStrategy",
    "VerificationStrategyRegistry",
    "VerificationEngine",
]
