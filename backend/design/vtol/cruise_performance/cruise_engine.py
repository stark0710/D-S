from .cruise_requirements import CruiseRequirements
from .cruise_profile import CruiseProfile
from .cruise_constraints import CruiseConstraints
from .cruise_result import CruiseResult
from .cruise_registry import CruiseRegistry
from .cruise_validator import CruiseValidator

class CruisePerformanceEngine:
    """
    Façade manager coordinating VTOL fixed-wing cruise efficiency evaluations.
    """
    def __init__(self, profile: CruiseProfile = None, constraints: CruiseConstraints = None):
        self.profile = profile or CruiseProfile()
        self.constraints = constraints or CruiseConstraints()

    def design(self, requirements: CruiseRequirements) -> CruiseResult:
        strategy = CruiseRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.design_cruise_performance(requirements, self.profile)
        
        errors = CruiseValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
