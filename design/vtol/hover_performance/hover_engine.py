from .hover_requirements import HoverRequirements
from .hover_profile import HoverProfile
from .hover_constraints import HoverConstraints
from .hover_result import HoverResult
from .hover_registry import HoverRegistry
from .hover_validator import HoverValidator

class HoverPerformanceEngine:
    """
    Façade orchestrator for sizing and validating VTOL hover performance metrics.
    """
    def __init__(self, profile: HoverProfile = None, constraints: HoverConstraints = None):
        self.profile = profile or HoverProfile()
        self.constraints = constraints or HoverConstraints()

    def design(self, requirements: HoverRequirements) -> HoverResult:
        strategy = HoverRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.design_hover_performance(requirements, self.profile)
        
        errors = HoverValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
