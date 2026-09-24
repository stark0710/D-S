from .transition_requirements import TransitionRequirements
from .transition_profile import TransitionProfile
from .transition_constraints import TransitionConstraints
from .transition_result import TransitionResult
from .transition_registry import TransitionRegistry
from .transition_validator import TransitionValidator

class TransitionFlightEngine:
    """
    Façade orchestrator for sizing and validating conversion flight margins.
    """
    def __init__(self, profile: TransitionProfile = None, constraints: TransitionConstraints = None):
        self.profile = profile or TransitionProfile()
        self.constraints = constraints or TransitionConstraints()

    def design(self, requirements: TransitionRequirements) -> TransitionResult:
        strategy = TransitionRegistry.get_strategy(requirements.mission_result.mission_profile.vtol_type)
        result = strategy.design_transition(requirements, self.profile)
        
        errors = TransitionValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
