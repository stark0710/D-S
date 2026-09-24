from typing import List
from .verification_result import VerificationResult
from .verification_constraints import VerificationConstraints

class VerificationValidator:
    """
    Validates verification scores against thresholds.
    """
    @staticmethod
    def validate(result: VerificationResult, constraints: VerificationConstraints) -> List[str]:
        warnings = []

        # Check compliance score
        score = result.verification_analysis.overall_compliance_score_pct
        if score < constraints.min_overall_compliance_score_pct:
            warnings.append(
                f"Sized compliance score ({score:.1f}%) "
                f"falls below target threshold ({constraints.min_overall_compliance_score_pct:.1f}%)"
            )

        # Check MTBF
        mtbf = result.reliability_verification.estimated_mtbf_hours
        if mtbf < constraints.min_reliability_mtbf_hours:
            warnings.append(
                f"Estimated MTBF ({mtbf:.1f} hrs) "
                f"is below safety requirement ({constraints.min_reliability_mtbf_hours:.1f} hrs)"
            )

        # Check stability margin
        margin = result.stability_verification.transition_stability_margin_pct
        if margin < constraints.min_stability_safety_margin_pct:
            warnings.append(
                f"Transition control stability margin ({margin:.1f}%) "
                f"is below safety margin ({constraints.min_stability_safety_margin_pct:.1f}%)"
            )

        return warnings
