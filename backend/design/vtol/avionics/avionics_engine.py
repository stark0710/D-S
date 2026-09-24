from .avionics_requirements import AvionicsRequirements
from .avionics_profile import AvionicsProfile
from .avionics_constraints import AvionicsConstraints
from .avionics_result import AvionicsResult
from .avionics_registry import AvionicsRegistry
from .avionics_validator import AvionicsValidator

class AvionicsEngine:
    """
    Facade orchestrator driving the VTOL Avionics Engineering Framework.
    """
    def __init__(self, profile: AvionicsProfile = None, constraints: AvionicsConstraints = None):
        self.profile = profile or AvionicsProfile()
        self.constraints = constraints or AvionicsConstraints()

    def design(self, requirements: AvionicsRequirements) -> AvionicsResult:
        strategy = AvionicsRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.design_avionics(requirements, self.profile)
        
        errors = AvionicsValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
