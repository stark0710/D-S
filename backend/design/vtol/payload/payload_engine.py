from .payload_requirements import PayloadRequirements
from .payload_profile import PayloadProfile
from .payload_constraints import PayloadConstraints
from .payload_result import PayloadResult
from .payload_registry import PayloadRegistry
from .payload_validator import PayloadValidator

class PayloadEngine:
    """
    Facade manager coordinating sized payloads and structural interfaces.
    """
    def __init__(self, profile: PayloadProfile = None, constraints: PayloadConstraints = None):
        self.profile = profile or PayloadProfile()
        self.constraints = constraints or PayloadConstraints()

    def design(self, requirements: PayloadRequirements) -> PayloadResult:
        strategy = PayloadRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.design_payload(requirements, self.profile)
        
        errors = PayloadValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
