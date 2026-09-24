from .verification_requirements import VerificationRequirements
from .verification_profile import VerificationProfile
from .verification_constraints import VerificationConstraints
from .verification_result import VerificationResult
from .verification_registry import VerificationRegistry
from .verification_validator import VerificationValidator

class VTOLVerificationEngine:
    """
    Façade manager coordinating complete VTOL aircraft certification verifications.
    """
    def __init__(self, profile: VerificationProfile = None, constraints: VerificationConstraints = None):
        self.profile = profile or VerificationProfile()
        self.constraints = constraints or VerificationConstraints()

    def design(self, requirements: VerificationRequirements) -> VerificationResult:
        strategy = VerificationRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.verify_design(requirements, self.profile)
        
        errors = VerificationValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
