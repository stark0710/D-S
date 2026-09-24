from dataclasses import dataclass, field
from typing import Any, Dict, List

from .mission_verifier import MissionVerification
from .performance_verifier import PerformanceVerification
from .stability_verifier import StabilityVerification
from .safety_verifier import SafetyVerification
from .reliability_verifier import ReliabilityVerification
from .environment_verifier import EnvironmentVerification
from .compliance_matrix import ComplianceMatrix
from .verification_analysis import VerificationAnalysis

@dataclass(slots=True)
class VerificationResult:
    """
    Consolidated outputs of the VTOL Mission Verification Framework.
    """
    mission_verification: MissionVerification
    performance_verification: PerformanceVerification
    stability_verification: StabilityVerification
    safety_verification: SafetyVerification
    reliability_verification: ReliabilityVerification
    environment_verification: EnvironmentVerification
    compliance_matrix: ComplianceMatrix
    verification_analysis: VerificationAnalysis

    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
