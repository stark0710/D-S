from .cad_requirements import CADRequirements
from .cad_profile import CADProfile
from .cad_constraints import CADConstraints
from .cad_result import CADResult
from .cad_registry import CADRegistry
from .cad_validator import CADValidator

class VTOLCADEngine:
    """
    Façade manager coordinating complete VTOL aircraft CAD assemblies generation.
    """
    def __init__(self, profile: CADProfile = None, constraints: CADConstraints = None):
        self.profile = profile or CADProfile()
        self.constraints = constraints or CADConstraints()

    def design(self, requirements: CADRequirements) -> CADResult:
        strategy = CADRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.generate_cad(requirements, self.profile)
        
        errors = CADValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
